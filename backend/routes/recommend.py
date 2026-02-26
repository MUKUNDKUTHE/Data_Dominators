# backend/routes/recommend.py
#
# Main recommendation endpoint
# Stitches all 4 services together
# Returns a complete farmer recommendation
# Updated: Added OLA Maps auto transit time calculation

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import sys, os, requests

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from services.mandi_service   import get_mandi_insight
from services.weather_service import get_weather_insight, get_coordinates
from services.crop_service    import get_crop_insight
from services.llm_service     import generate_recommendation

router = APIRouter()

# ─────────────────────────────────────────
# OLA MAPS CONFIG
# ─────────────────────────────────────────
OLA_MAPS_API_KEY   = os.getenv("OLA_MAPS_API_KEY")
OLA_DIRECTIONS_URL = "https://api.olamaps.io/routing/v1/directions"
OLA_GEOCODE_URL    = "https://api.olamaps.io/places/v1/geocode"


# ─────────────────────────────────────────
# REQUEST MODEL
# ─────────────────────────────────────────
class RecommendRequest(BaseModel):
    # Crop info
    crop:     str = Field(...,              example="Tomato")
    variety:  str = Field(default="Local",  example="Local")
    grade:    str = Field(default="Medium", example="Medium")

    # Location
    state:    str = Field(..., example="Maharashtra")
    district: str = Field(..., example="Pune")
    market:   str = Field(..., example="Pune")

    # Harvest date
    harvest_date: str = Field(..., example="2025-10-15")

    # Soil inputs
    ph:          float = Field(default=6.5,   example=6.5)
    soil_ec:     float = Field(default=0.6,   example=0.6)
    phosphorus:  float = Field(default=20.0,  example=20.0)
    potassium:   float = Field(default=150.0, example=150.0)
    urea:        float = Field(default=50.0,  example=50.0)
    tsp:         float = Field(default=22.0,  example=22.0)
    mop:         float = Field(default=30.0,  example=30.0)
    moisture:    float = Field(default=68.0,  example=68.0)
    temperature: float = Field(default=72.0,  example=72.0)

    # Storage info
    storage_type: str = Field(default="basic_shed", example="basic_shed")

    # Transit — 0 = auto-calculate via OLA Maps
    transit_hours: float = Field(
        default=0.0,
        example=0.0,
        description="Hours to market. Set 0 to auto-calculate via OLA Maps."
    )


# ─────────────────────────────────────────
# RESPONSE MODEL
# ─────────────────────────────────────────
class RecommendResponse(BaseModel):
    success:          bool
    crop:             str
    state:            str
    recommendation:   str
    price_prediction: dict
    price_trend:      dict
    best_markets:     dict
    weather:          dict
    crop_suitability: dict
    micronutrient:    dict
    spoilage:         dict
    transit_info:     dict


# ─────────────────────────────────────────
# OLA MAPS — GEOCODE LOCATION
# ─────────────────────────────────────────
def geocode_location(location: str) -> Optional[dict]:
    if not OLA_MAPS_API_KEY:
        return None
    try:
        response = requests.get(
            OLA_GEOCODE_URL,
            params={"address": f"{location}, India", "api_key": OLA_MAPS_API_KEY},
            timeout=5
        )
        data = response.json()
        if data.get("geocodingResults"):
            loc = data["geocodingResults"][0]["geometry"]["location"]
            return {"lat": loc["lat"], "lon": loc["lng"]}
    except Exception as e:
        print(f"⚠️ OLA geocode failed: {e}")
    return None


# ─────────────────────────────────────────
# OLA MAPS — GET TRANSIT TIME
# Returns real driving time between
# farmer district and best market
# ─────────────────────────────────────────
def get_transit_time_ola(
    origin_district: str,
    origin_state:    str,
    dest_market:     str,
    dest_state:      str
) -> dict:
    """
    Calculates real driving time using OLA Maps Directions API.
    Falls back to 6hr default if API unavailable.
    """
    default_result = {
        "transit_hours":  6.0,
        "distance_km":    0,
        "source":         "default",
        "route_summary":  "Transit time estimated at 6 hours (set OLA_MAPS_API_KEY for real data)"
    }

    if not OLA_MAPS_API_KEY:
        print("⚠️ OLA_MAPS_API_KEY not set. Using 6hr default.")
        return default_result

    try:
        # Get coordinates — OLA Maps first, fallback to OpenWeather geocoding
        origin_coords = geocode_location(f"{origin_district}, {origin_state}") or \
                        get_coordinates(origin_district, origin_state)
        dest_coords   = geocode_location(f"{dest_market}, {dest_state}") or \
                        get_coordinates(dest_market, dest_state)

        if not origin_coords or not dest_coords:
            return default_result

        origin_str = f"{origin_coords['lat']},{origin_coords['lon']}"
        dest_str   = f"{dest_coords['lat']},{dest_coords['lon']}"

        # Call OLA Directions API
        response = requests.get(
            OLA_DIRECTIONS_URL,
            params={
                "origin":      origin_str,
                "destination": dest_str,
                "api_key":     OLA_MAPS_API_KEY
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        routes = data.get("routes", [])
        if not routes:
            return default_result

        leg             = routes[0]["legs"][0]
        duration_secs   = leg.get("duration", 21600)
        distance_meters = leg.get("distance", 0)

        transit_hours = round(duration_secs / 3600, 1)
        distance_km   = round(distance_meters / 1000, 1)

        # Plain language summary
        if transit_hours < 2:
            summary = f"Close market — {transit_hours} hrs drive ({distance_km} km). Low transit risk."
        elif transit_hours < 4:
            summary = f"Moderate distance — {transit_hours} hrs ({distance_km} km). Plan early morning departure."
        else:
            summary = f"Long distance — {transit_hours} hrs ({distance_km} km). Consider overnight storage before transport."

        print(f"✅ OLA Maps: {origin_district} → {dest_market} = {transit_hours}hrs ({distance_km}km)")

        return {
            "transit_hours":  transit_hours,
            "distance_km":    distance_km,
            "source":         "ola_maps",
            "route_summary":  summary
        }

    except requests.exceptions.RequestException as e:
        print(f"⚠️ OLA Maps API error: {e}. Using default.")
        return default_result
    except Exception as e:
        print(f"⚠️ Transit error: {e}. Using default.")
        return default_result


# ─────────────────────────────────────────
# MAIN ENDPOINT
# POST /api/recommend
# ─────────────────────────────────────────
@router.post("/recommend", response_model=RecommendResponse)
async def recommend(request: RecommendRequest):
    """
    Master recommendation endpoint.
    Calls all 4 services + OLA Maps transit →
    generates LLM plain language recommendation.
    """
    try:

        # ── Step 1: Mandi Price Intelligence ──
        mandi_result = get_mandi_insight(
            state     = request.state,
            district  = request.district,
            market    = request.market,
            commodity = request.crop,
            variety   = request.variety,
            grade     = request.grade,
            date      = request.harvest_date
        )

        # ── Step 2: Weather Intelligence ──
        weather_result = get_weather_insight(
            city  = request.district,
            state = request.state
        )

        # ── Step 3: Auto-calculate Transit Time ──
        best_market = mandi_result["best_markets"].get("best_market", request.market)

        if request.transit_hours == 0:
            # Auto-calculate to BEST market (not just the requested market)
            transit_info  = get_transit_time_ola(
                origin_district = request.district,
                origin_state    = request.state,
                dest_market     = best_market,
                dest_state      = request.state
            )
            transit_hours = transit_info["transit_hours"]
        else:
            transit_hours = request.transit_hours
            transit_info  = {
                "transit_hours":  transit_hours,
                "distance_km":    0,
                "source":         "farmer_provided",
                "route_summary":  f"Transit time provided: {transit_hours} hours to market"
            }

        # ── Step 4: Crop + Soil Intelligence ──
        crop_result = get_crop_insight(
            crop            = request.crop,
            district        = request.district,
            ph              = request.ph,
            soil_ec         = request.soil_ec,
            phosphorus      = request.phosphorus,
            potassium       = request.potassium,
            urea            = request.urea,
            tsp             = request.tsp,
            mop             = request.mop,
            moisture        = request.moisture,
            temperature     = request.temperature,
            storage_type    = request.storage_type,
            transit_hours   = transit_hours,
            spoilage_factor = weather_result["current"].get("spoilage_factor", 1.0)
        )

        # ── Step 5: Build LLM Context ──
        price_data   = mandi_result["price_prediction"]
        trend_data   = mandi_result["price_trend"]
        market_data  = mandi_result["best_markets"]
        weather_data = weather_result["current"]
        forecast     = weather_result["forecast"]
        suitability  = crop_result["suitability"]
        spoilage     = crop_result["spoilage"]

        llm_context = {
            "crop":               request.crop,
            "state":              request.state,
            "district":           request.district,
            "predicted_price":    price_data.get("predicted_price", "N/A"),
            "price_trend":        f"{trend_data.get('trend', 'stable')} "
                                  f"({trend_data.get('change_pct', 0)}%)",
            "best_market":        market_data.get("best_market", request.market),
            "best_market_price":  market_data.get("best_price", "N/A"),
            "harvest_window":     f"Around {request.harvest_date}",
            "best_harvest_day":   forecast.get("best_day", request.harvest_date),
            "weather":            weather_data.get("weather_summary", "N/A"),
            "harvest_risk":       weather_data.get("harvest_risk", "Low"),
            "spoilage_risk":      spoilage.get("risk_level", "Low"),
            "days_safe":          spoilage.get("days_safe", 7),
            "transit_hours":      transit_hours,
            "transit_summary":    transit_info.get("route_summary", ""),
            "preservation_actions": ", ".join([
                a["action"] for a in spoilage.get("actions", [])[:3]
            ]),
            "is_crop_suitable":   suitability.get("is_suitable", False),
            "recommended_crop":   suitability.get("recommended_crop", request.crop),
            "suitability_score":  suitability.get("suitability_score", 50)
        }

        # ── Step 6: Generate Plain Language Recommendation ──
        recommendation = generate_recommendation(llm_context)

        # ── Step 7: Return Full Response ──
        return RecommendResponse(
            success          = True,
            crop             = request.crop,
            state            = request.state,
            recommendation   = recommendation,
            price_prediction = price_data,
            price_trend      = trend_data,
            best_markets     = market_data,
            weather          = weather_data,
            crop_suitability = suitability,
            micronutrient    = crop_result["micronutrient"],
            spoilage         = spoilage,
            transit_info     = transit_info
        )

    except Exception as e:
        raise HTTPException(
            status_code = 500,
            detail      = f"Recommendation failed: {str(e)}"
        )


# ─────────────────────────────────────────
# QUICK PRICE ENDPOINT
# GET /api/price
# ─────────────────────────────────────────
@router.get("/price")
async def quick_price(
    crop: str, state: str, district: str,
    market: str, date: str,
    variety: str = "Local", grade: str = "Medium"
):
    try:
        result = get_mandi_insight(
            state=state, district=district, market=market,
            commodity=crop, variety=variety, grade=grade, date=date
        )
        return {"success": True, **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────
# TRANSIT TIME ENDPOINT
# GET /api/transit?origin=Pune&state=Maharashtra&dest=Panvel+APMC
# ─────────────────────────────────────────
@router.get("/transit")
async def transit(origin: str, state: str, dest: str):
    """Returns live transit time between farmer location and market."""
    try:
        result = get_transit_time_ola(
            origin_district=origin, origin_state=state,
            dest_market=dest,       dest_state=state
        )
        return {"success": True, **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))