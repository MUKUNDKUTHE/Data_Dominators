# backend/routes/recommend.py
#
# Main recommendation endpoint
# Stitches all 4 services together
# Returns a complete farmer recommendation

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from services.mandi_service   import get_mandi_insight
from services.weather_service import get_weather_insight
from services.crop_service    import get_crop_insight
from services.llm_service     import generate_recommendation

router = APIRouter()


# ─────────────────────────────────────────
# REQUEST MODEL
# What the farmer/frontend sends
# ─────────────────────────────────────────
class RecommendRequest(BaseModel):
    # Crop info
    crop:       str = Field(..., example="Tomato")
    variety:    str = Field(default="Local", example="Local")
    grade:      str = Field(default="Medium", example="Medium")

    # Location
    state:      str = Field(..., example="Maharashtra")
    district:   str = Field(..., example="Pune")
    market:     str = Field(..., example="Pune")

    # Harvest date
    harvest_date: str = Field(..., example="2025-10-15")

    # Soil inputs (from Plant_Parameters dataset)
    ph:           float = Field(default=6.5,   example=6.5)
    soil_ec:      float = Field(default=0.6,   example=0.6)
    phosphorus:   float = Field(default=20.0,  example=20.0)
    potassium:    float = Field(default=150.0, example=150.0)
    urea:         float = Field(default=50.0,  example=50.0)
    tsp:          float = Field(default=22.0,  example=22.0)
    mop:          float = Field(default=30.0,  example=30.0)
    moisture:     float = Field(default=68.0,  example=68.0)
    temperature:  float = Field(default=72.0,  example=72.0)

    # Storage info
    storage_type:  str   = Field(default="basic_shed", example="basic_shed")
    transit_hours: float = Field(default=6.0,          example=6.0)


# ─────────────────────────────────────────
# RESPONSE MODEL
# What the API returns
# ─────────────────────────────────────────
class RecommendResponse(BaseModel):
    success:         bool
    crop:            str
    state:           str
    recommendation:  str          # plain language from LLM
    price_prediction: dict
    price_trend:      dict
    best_markets:     dict
    weather:          dict
    crop_suitability: dict
    micronutrient:    dict
    spoilage:         dict


# ─────────────────────────────────────────
# MAIN ENDPOINT
# POST /api/recommend
# ─────────────────────────────────────────
@router.post("/recommend", response_model=RecommendResponse)
async def recommend(request: RecommendRequest):
    """
    Master recommendation endpoint.

    Takes farmer inputs → calls all 4 services →
    generates plain language recommendation via LLM →
    returns complete structured response.
    """
    try:

        # ── Step 1: Mandi Price Intelligence ──
        mandi_result = get_mandi_insight(
            state      = request.state,
            district   = request.district,
            market     = request.market,
            commodity  = request.crop,
            variety    = request.variety,
            grade      = request.grade,
            date       = request.harvest_date
        )

        # ── Step 2: Weather Intelligence ──
        weather_result = get_weather_insight(
            city  = request.district,
            state = request.state
        )

        # ── Step 3: Crop + Soil Intelligence ──
        crop_result = get_crop_insight(
            crop          = request.crop,
            district      = request.district,
            ph            = request.ph,
            soil_ec       = request.soil_ec,
            phosphorus    = request.phosphorus,
            potassium     = request.potassium,
            urea          = request.urea,
            tsp           = request.tsp,
            mop           = request.mop,
            moisture      = request.moisture,
            temperature   = request.temperature,
            storage_type  = request.storage_type,
            transit_hours = request.transit_hours,
            spoilage_factor = weather_result["current"].get("spoilage_factor", 1.0)
        )

        # ── Step 4: Build LLM Context ──
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
            "preservation_actions": ", ".join([
                a["action"] for a in spoilage.get("actions", [])[:3]
            ]),
            "is_crop_suitable":   suitability.get("is_suitable", False),
            "recommended_crop":   suitability.get("recommended_crop", request.crop),
            "suitability_score":  suitability.get("suitability_score", 50)
        }

        # ── Step 5: Generate Plain Language Recommendation ──
        recommendation = generate_recommendation(llm_context)

        # ── Step 6: Return Full Response ──
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
            spoilage         = spoilage
        )

    except Exception as e:
        raise HTTPException(
            status_code = 500,
            detail      = f"Recommendation failed: {str(e)}"
        )


# ─────────────────────────────────────────
# QUICK PRICE CHECK ENDPOINT
# GET /api/price?crop=Tomato&state=Maharashtra&date=2025-10-15
# Lightweight endpoint for just price prediction
# ─────────────────────────────────────────
@router.get("/price")
async def quick_price(
    crop:     str,
    state:    str,
    district: str,
    market:   str,
    date:     str,
    variety:  str = "Local",
    grade:    str = "Medium"
):
    """
    Quick price prediction endpoint.
    Lighter than /recommend — just returns price.
    """
    try:
        result = get_mandi_insight(
            state     = state,
            district  = district,
            market    = market,
            commodity = crop,
            variety   = variety,
            grade     = grade,
            date      = date
        )
        return {"success": True, **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))