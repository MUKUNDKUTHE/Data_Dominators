from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Any, Tuple


SOURCE_LABELS = {
    "weather": "Weather",
    "mandi_price": "Mandi price trend",
    "soil": "Soil health",
    "spoilage": "Storage and transit risk",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _confidence_label(score: float) -> str:
    if score >= 0.75:
        return "High"
    if score >= 0.45:
        return "Medium"
    return "Low"


def _to_reason_line(item: Dict[str, Any]) -> str:
    source = SOURCE_LABELS.get(str(item.get("source", "")).strip().lower(), "Signal")
    reason = str(item.get("reason", "")).strip()
    if reason:
        return f"{source}: {reason}"
    metric = str(item.get("metric", "")).strip()
    value = item.get("value", "")
    if metric and value != "":
        return f"{source}: {metric} is {value}"
    return f"{source}: Important signal detected"


def _rank_evidence(evidence: List[Dict[str, Any]], top_n: int = 3) -> List[Dict[str, Any]]:
    scored: List[Tuple[float, Dict[str, Any]]] = []
    for item in evidence:
        impact = float(item.get("impact", 0.0))
        scored.append((impact, item))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [item for _, item in scored[:top_n]]


def build_explainable_response(
    recommendation: str,
    evidence: List[Dict[str, Any]],
    risks: List[str] | None = None,
    alternative: str | None = None,
    confidence_score: float | None = None,
    data_last_updated: str | None = None,
) -> Dict[str, Any]:
    """
    Build farmer-friendly explainable output.

    Evidence item format (example):
    {
      "source": "weather" | "mandi_price" | "soil" | "spoilage",
      "impact": 0.0 to 1.0,
      "reason": "Heavy rain likely after 3 days"
    }
    """
    safe_recommendation = str(recommendation).strip()
    safe_risks = risks or []
    safe_alternative = (
        alternative.strip()
        if isinstance(alternative, str) and alternative.strip()
        else "If immediate action is not possible, use shaded ventilated storage and sell at the nearest mandi within 48 hours."
    )

    top_items = _rank_evidence(evidence, top_n=3)
    top_reasons = [_to_reason_line(item) for item in top_items]

    if confidence_score is None:
        if top_items:
            confidence_score = sum(float(item.get("impact", 0.0)) for item in top_items) / len(top_items)
        else:
            confidence_score = 0.35

    response = {
        "recommendation": safe_recommendation,
        "top_reasons": top_reasons,
        "confidence": _confidence_label(float(confidence_score)),
        "risks": [str(r).strip() for r in safe_risks if str(r).strip()],
        "alternative": safe_alternative,
        "data_last_updated": data_last_updated or _now_iso(),
    }

    return response


def validate_explainable_response(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Hard validation gate before API response is returned.
    Returns (is_valid, errors).
    """
    errors: List[str] = []

    required_fields = [
        "recommendation",
        "top_reasons",
        "confidence",
        "alternative",
        "data_last_updated",
    ]

    for field in required_fields:
        if field not in payload:
            errors.append(f"Missing field: {field}")

    if "top_reasons" in payload:
        reasons = payload.get("top_reasons", [])
        if not isinstance(reasons, list) or len(reasons) == 0:
            errors.append("top_reasons must contain at least one reason")

    if "confidence" in payload and payload.get("confidence") not in ["High", "Medium", "Low"]:
        errors.append("confidence must be one of: High, Medium, Low")

    if "recommendation" in payload and not str(payload.get("recommendation", "")).strip():
        errors.append("recommendation cannot be empty")

    if "alternative" in payload and not str(payload.get("alternative", "")).strip():
        errors.append("alternative cannot be empty")

    return (len(errors) == 0, errors)


def build_and_validate(
    recommendation: str,
    evidence: List[Dict[str, Any]],
    risks: List[str] | None = None,
    alternative: str | None = None,
    confidence_score: float | None = None,
    data_last_updated: str | None = None,
) -> Dict[str, Any]:
    """
    Convenience helper for route handlers.
    Raises ValueError if output is not explainable-complete.
    """
    payload = build_explainable_response(
        recommendation=recommendation,
        evidence=evidence,
        risks=risks,
        alternative=alternative,
        confidence_score=confidence_score,
        data_last_updated=data_last_updated,
    )

    is_valid, errors = validate_explainable_response(payload)
    if not is_valid:
        raise ValueError("Explainability validation failed: " + "; ".join(errors))

    return payload


def evidence_from_context(context: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Adapter that converts existing AgriChain context keys into evidence items.
    This keeps integration local to this file so other files need no edits.
    """
    evidence: List[Dict[str, Any]] = []

    weather = str(context.get("weather", "")).strip()
    if weather:
        impact = 0.7 if any(word in weather.lower() for word in ["rain", "storm", "heatwave", "high humidity"]) else 0.45
        evidence.append(
            {
                "source": "weather",
                "impact": impact,
                "reason": weather,
            }
        )

    trend = str(context.get("price_trend", "")).strip()
    predicted_price = context.get("predicted_price")
    if trend or predicted_price is not None:
        parts: List[str] = []
        if trend:
            parts.append(f"Price trend is {trend}")
        if predicted_price is not None:
            parts.append(f"Expected price is ₹{predicted_price}/quintal")
        evidence.append(
            {
                "source": "mandi_price",
                "impact": 0.8 if "rising" in trend.lower() else 0.6,
                "reason": ", ".join(parts),
            }
        )

    soil_reason_parts: List[str] = []
    if context.get("soil_ph") is not None:
        soil_reason_parts.append(f"soil pH is {context.get('soil_ph')}")
    if context.get("soil_moisture") is not None:
        soil_reason_parts.append(f"soil moisture is {context.get('soil_moisture')}%")
    if soil_reason_parts:
        evidence.append(
            {
                "source": "soil",
                "impact": 0.55,
                "reason": " and ".join(soil_reason_parts),
            }
        )

    spoilage_risk = str(context.get("spoilage_risk", "")).strip()
    transit_hours = context.get("transit_hours")
    days_safe = context.get("days_safe")
    if spoilage_risk or transit_hours is not None or days_safe is not None:
        parts: List[str] = []
        if spoilage_risk:
            parts.append(f"spoilage risk is {spoilage_risk}")
        if transit_hours is not None:
            parts.append(f"transit time is {transit_hours} hours")
        if days_safe is not None:
            parts.append(f"safe selling window is {days_safe} days")
        evidence.append(
            {
                "source": "spoilage",
                "impact": 0.75 if spoilage_risk.lower() == "high" else 0.5,
                "reason": ", ".join(parts),
            }
        )

    if not evidence:
        evidence.append(
            {
                "source": "weather",
                "impact": 0.35,
                "reason": "Limited live signals available; recommendation based on available baseline inputs",
            }
        )

    return evidence


def build_explainable_from_context(
    recommendation: str,
    context: Dict[str, Any],
    alternative: str | None = None,
    data_last_updated: str | None = None,
) -> Dict[str, Any]:
    """
    One-call adapter: take existing recommendation + context and return
    explainable farmer-ready payload.
    """
    evidence = evidence_from_context(context)

    risks: List[str] = []
    spoilage_risk = str(context.get("spoilage_risk", "")).strip().lower()
    if spoilage_risk == "high":
        risks.append("High spoilage chance if sale is delayed")
    elif spoilage_risk == "medium":
        risks.append("Moderate spoilage chance in current storage/transit conditions")

    weather = str(context.get("weather", "")).strip().lower()
    if any(word in weather for word in ["heavy rain", "storm", "extreme heat"]):
        risks.append("Weather volatility may shift harvest or transit timing")

    return build_and_validate(
        recommendation=recommendation,
        evidence=evidence,
        risks=risks,
        alternative=alternative,
        confidence_score=None,
        data_last_updated=data_last_updated,
    )


def generate_and_explain(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Optional connector: generates recommendation using existing llm_service
    and immediately wraps it with explainability.
    This function keeps integration centralized in this file.
    """
    from services.llm_service import generate_recommendation

    recommendation_text = generate_recommendation(context)
    return build_explainable_from_context(
        recommendation=recommendation_text,
        context=context,
        alternative=context.get("alternative"),
        data_last_updated=context.get("data_last_updated"),
    )