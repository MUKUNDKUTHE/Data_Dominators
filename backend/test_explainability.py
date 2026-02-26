# Test explainability service

from services.explainability_service import (
    build_explainable_from_context,
    generate_and_explain,
    build_explainable_response
)

print("=" * 60)
print("  AgriChain Explainability Service Test")
print("=" * 60)

# ─────────────────────────────────────────
# TEST 1 — High Risk Scenario
# ─────────────────────────────────────────
print("\n📊 TEST 1: High Spoilage Risk + Rising Prices")
print("-" * 60)

context = {
    "crop": "Tomato",
    "district": "Pune",
    "state": "Maharashtra",
    "predicted_price": 3200,
    "price_trend": "Rising (12%)",
    "weather": "Heavy rain expected after 3 days",
    "harvest_risk": "Medium",
    "spoilage_risk": "High",
    "days_safe": 2,
    "transit_hours": 8,
    "soil_ph": 6.5,
    "soil_moisture": 68
}

recommendation = (
    "Harvest tomatoes within 48 hours before rain starts. "
    "Sell immediately at Pune mandi where prices are rising at ₹3,200/quintal. "
    "Store in shaded area with good ventilation until sale."
)

result = build_explainable_from_context(
    recommendation=recommendation,
    context=context,
    alternative="If you cannot harvest in 48h, apply mulching and delay harvest by 5 days after rain stops"
)

print("\n✅ Recommendation:")
print(f"   {result['recommendation']}")

print("\n🔍 Top 3 Reasons (Why this recommendation):")
for i, reason in enumerate(result['top_reasons'], 1):
    print(f"   {i}. {reason}")

print(f"\n📈 Confidence: {result['confidence']}")

if result['risks']:
    print(f"\n⚠️  Risks:")
    for risk in result['risks']:
        print(f"   • {risk}")

print(f"\n🔄 Alternative Action:")
print(f"   {result['alternative']}")

print(f"\n🕐 Data Last Updated: {result['data_last_updated']}")


# ─────────────────────────────────────────
# TEST 2 — Low Risk Scenario
# ─────────────────────────────────────────
print("\n\n📊 TEST 2: Low Risk + Stable Prices")
print("-" * 60)

context2 = {
    "crop": "Wheat",
    "district": "Ludhiana",
    "state": "Punjab",
    "predicted_price": 2100,
    "price_trend": "Stable (0%)",
    "weather": "Clear skies, optimal temperature",
    "harvest_risk": "Low",
    "spoilage_risk": "Low",
    "days_safe": 30,
    "transit_hours": 4,
}

recommendation2 = (
    "Harvest wheat in 7-10 days when moisture is below 14%. "
    "Sell at Ludhiana mandi at ₹2,100/quintal or store for up to 30 days. "
    "Prices are stable, no urgency to rush sale."
)

result2 = build_explainable_from_context(
    recommendation=recommendation2,
    context=context2
)

print("\n✅ Recommendation:")
print(f"   {result2['recommendation']}")

print("\n🔍 Top 3 Reasons:")
for i, reason in enumerate(result2['top_reasons'], 1):
    print(f"   {i}. {reason}")

print(f"\n📈 Confidence: {result2['confidence']}")

if result2['risks']:
    print(f"\n⚠️  Risks:")
    for risk in result2['risks']:
        print(f"   • {risk}")
else:
    print("\n✅ No significant risks detected")

print(f"\n🔄 Alternative Action:")
print(f"   {result2['alternative']}")


# ─────────────────────────────────────────
# TEST 3 — Manual Evidence Building
# ─────────────────────────────────────────
print("\n\n📊 TEST 3: Manual Evidence with Custom Impact Scores")
print("-" * 60)

evidence = [
    {
        "source": "weather",
        "impact": 0.9,  # High impact
        "reason": "Cyclone warning in 48 hours - harvest immediately"
    },
    {
        "source": "mandi_price",
        "impact": 0.7,
        "reason": "Price peak detected - best to sell now"
    },
    {
        "source": "spoilage",
        "impact": 0.8,
        "reason": "Open air storage - very high spoilage risk"
    },
    {
        "source": "soil",
        "impact": 0.3,  # Lower impact
        "reason": "Soil moisture adequate"
    }
]

result3 = build_explainable_response(
    recommendation="URGENT: Harvest all crops within 24 hours and sell immediately",
    evidence=evidence,
    risks=["Total crop loss if cyclone hits", "Road access may be blocked"],
    alternative="If harvest impossible, secure with tarpaulin and anchor firmly",
    confidence_score=0.85  # High confidence
)

print("\n✅ Recommendation:")
print(f"   {result3['recommendation']}")

print("\n🔍 Top 3 Reasons (Ranked by Impact):")
for i, reason in enumerate(result3['top_reasons'], 1):
    print(f"   {i}. {reason}")

print(f"\n📈 Confidence: {result3['confidence']}")

print(f"\n⚠️  Risks:")
for risk in result3['risks']:
    print(f"   • {risk}")

print(f"\n🔄 Alternative Action:")
print(f"   {result3['alternative']}")


# ─────────────────────────────────────────
# TEST 4 — Validation
# ─────────────────────────────────────────
print("\n\n📊 TEST 4: Validation Check")
print("-" * 60)

from services.explainability_service import validate_explainable_response

# Valid payload
valid_payload = result

is_valid, errors = validate_explainable_response(valid_payload)
print(f"\n✅ Valid Payload: {is_valid}")
if errors:
    print(f"   Errors: {errors}")

# Invalid payload (missing fields)
invalid_payload = {
    "recommendation": "Harvest now",
    "top_reasons": []  # Empty reasons - INVALID
}

is_valid2, errors2 = validate_explainable_response(invalid_payload)
print(f"\n❌ Invalid Payload: {is_valid2}")
print(f"   Errors:")
for err in errors2:
    print(f"   • {err}")


print("\n" + "=" * 60)
print("  All Tests Complete!")
print("=" * 60)
