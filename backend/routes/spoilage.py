# backend/routes/spoilage.py
#
# Spoilage risk endpoint
# Standalone endpoint for post-harvest spoilage assessment

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from services.crop_service    import get_spoilage_risk, get_micronutrient_warnings
from services.weather_service import get_current_weather
from services.llm_service     import generate_spoilage_advice

router = APIRouter()


# ─────────────────────────────────────────
# REQUEST MODEL
# ─────────────────────────────────────────
class SpoilageRequest(BaseModel):
    crop:          str   = Field(...,          example="Tomato")
    district:      str   = Field(...,          example="Pune")
    state:         str   = Field(...,          example="Maharashtra")
    storage_type:  str   = Field(default="basic_shed", example="basic_shed")
    transit_hours: float = Field(default=6.0,  example=6.0)

    # Optional — if not provided, fetched from OpenWeather
    temperature:   float = Field(default=None, example=30.0)
    humidity:      float = Field(default=None, example=65.0)


# ─────────────────────────────────────────
# SPOILAGE ENDPOINT
# POST /api/spoilage
# ─────────────────────────────────────────
@router.post("/spoilage")
async def spoilage(request: SpoilageRequest):
    """
    Standalone spoilage risk assessment.

    If temperature/humidity not provided,
    fetches live weather from OpenWeather API.

    Returns:
        risk_level, days_safe, preservation actions,
        micronutrient warnings, LLM plain language advice
    """
    try:
        # ── Get weather if not provided ──
        if request.temperature is None or request.humidity is None:
            weather = get_current_weather(request.district, request.state)
            temperature = weather.get("temperature", 30.0)
            humidity    = weather.get("humidity",    65.0)
            spoilage_factor = weather.get("spoilage_factor", 1.0)
        else:
            temperature     = request.temperature
            humidity        = request.humidity
            spoilage_factor = 1.0

        # ── Calculate spoilage risk ──
        spoilage_result = get_spoilage_risk(
            crop            = request.crop,
            storage_type    = request.storage_type,
            transit_hours   = request.transit_hours,
            temperature     = temperature,
            humidity        = humidity,
            spoilage_factor = spoilage_factor
        )

        # ── Get micronutrient warnings ──
        micro_result = get_micronutrient_warnings(request.district)

        # ── Generate LLM advice ──
        llm_context = {
            "crop":          request.crop,
            "storage_type":  request.storage_type,
            "transit_hours": request.transit_hours,
            "temperature":   f"{temperature}°C",
            "humidity":      f"{humidity}%",
            "spoilage_score": spoilage_result["risk_score"]
        }
        llm_advice = generate_spoilage_advice(llm_context)

        return {
            "success":       True,
            "crop":          request.crop,
            "district":      request.district,
            "spoilage":      spoilage_result,
            "micronutrient": micro_result,
            "advice":        llm_advice,
            "weather_used":  {
                "temperature":    temperature,
                "humidity":       humidity,
                "spoilage_factor": spoilage_factor
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────
# STORAGE TYPES INFO ENDPOINT
# GET /api/storage-types
# Helps frontend show dropdown options
# ─────────────────────────────────────────
@router.get("/storage-types")
def storage_types():
    return {
        "storage_types": [
            {
                "value":       "open_air",
                "label":       "Open Air",
                "description": "No protection from weather",
                "risk":        "High"
            },
            {
                "value":       "basic_shed",
                "label":       "Basic Shed",
                "description": "Simple covered storage",
                "risk":        "Medium"
            },
            {
                "value":       "cool_storage",
                "label":       "Cool Storage",
                "description": "Ventilated cool room",
                "risk":        "Low"
            },
            {
                "value":       "cold_storage",
                "label":       "Cold Storage",
                "description": "Temperature controlled facility",
                "risk":        "Very Low"
            }
        ]
    }


# ─────────────────────────────────────────
# CROPS INFO ENDPOINT
# GET /api/crops
# Returns all supported crops with shelf life
# ─────────────────────────────────────────
@router.get("/crops")
def get_crops():
    from services.crop_service import CROP_PROFILES
    crops = []
    for crop, profile in CROP_PROFILES.items():
        if crop != "Default":
            crops.append({
                "name":            crop,
                "shelf_life_days": profile["shelf_life_days"],
                "storage_tip":     profile["storage_tip"]
            })
    crops.sort(key=lambda x: x["name"])
    return {"crops": crops}