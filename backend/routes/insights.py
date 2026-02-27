# backend/routes/insights.py
#
# New insight endpoints:
#   POST /api/arrival-prediction  — when will arrival surge crash prices?
#   POST /api/loss-risk           — how much money at risk from spoilage?
#   POST /api/bypass-score        — should farmer skip the Arthiya?
#   POST /api/grade-crop          — AI photo grading of produce quality

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from services.mandi_service import get_arrival_surge_prediction, get_bypass_score
from services.crop_service  import calculate_loss_risk
from services.llm_service   import grade_crop_from_image

router = APIRouter()


# ─────────────────────────────────────────
# REQUEST MODELS
# ─────────────────────────────────────────

class ArrivalPredictionRequest(BaseModel):
    crop:  str
    state: str
    date:  Optional[str] = None


class LossRiskRequest(BaseModel):
    crop:              str
    quantity_quintals: float = Field(default=10.0, example=10.0)
    predicted_price:   float = Field(..., example=1500.0)
    spoilage_score:    int   = Field(..., example=45)
    storage_type:      str   = Field(default="basic_shed", example="basic_shed")


class BypassScoreRequest(BaseModel):
    crop:              str
    state:             str
    quantity_quintals: float = Field(default=10.0, example=10.0)
    predicted_price:   float = Field(..., example=1500.0)
    price_trend:       str   = Field(default="stable", example="rising")


class GradeRequest(BaseModel):
    crop:         str
    image_base64: str   # base64-encoded JPEG image


# ─────────────────────────────────────────
# POST /api/arrival-prediction
# ─────────────────────────────────────────
@router.post("/arrival-prediction")
async def arrival_prediction(request: ArrivalPredictionRequest):
    """
    Predicts whether this week or coming weeks will see a high-volume
    arrival surge for the given crop+state, with historic price impact.
    """
    try:
        return get_arrival_surge_prediction(request.crop, request.state, request.date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────
# POST /api/loss-risk
# ─────────────────────────────────────────
@router.post("/loss-risk")
async def loss_risk(request: LossRiskRequest):
    """
    Given quantity + predicted price + spoilage score, returns:
    - Expected financial loss in rupees
    - Cost of upgrading storage
    - Money saved by upgrading
    - ROI of the upgrade
    """
    try:
        return calculate_loss_risk(
            crop              = request.crop,
            quantity_quintals = request.quantity_quintals,
            predicted_price   = request.predicted_price,
            spoilage_score    = request.spoilage_score,
            storage_type      = request.storage_type
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────
# POST /api/bypass-score
# ─────────────────────────────────────────
@router.post("/bypass-score")
async def bypass_score(request: BypassScoreRequest):
    """
    Scores (out of 10) whether skipping the commission agent (Arthiya)
    is financially worthwhile for this farmer's situation.
    """
    try:
        return get_bypass_score(
            crop              = request.crop,
            state             = request.state,
            quantity_quintals = request.quantity_quintals,
            predicted_price   = request.predicted_price,
            price_trend       = request.price_trend
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────
# POST /api/grade-crop
# ─────────────────────────────────────────
@router.post("/grade-crop")
async def grade_crop(request: GradeRequest):
    """
    Accepts a base64-encoded JPEG photo of produce.
    Returns AGMARK grade (A/B/C), confidence, and actionable tip
    using Groq's llama-3.2-11b-vision model.
    """
    try:
        return grade_crop_from_image(request.image_base64, request.crop)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
