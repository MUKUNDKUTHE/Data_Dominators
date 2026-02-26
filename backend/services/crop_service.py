# backend/services/crop_service.py
#
# Dataset: Plant_Parameters.csv (100,000 rows, 70+ crops)
# Columns: pH, Soil EC, Phosphorus, Potassium,
#          Urea, T.S.P, M.O.P, Moisture, Temperature, Plant Type
#
# Place at: backend/data/soil/Plant_Parameters.csv

import os
import pickle
import warnings
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


from services.crop_profiles import (
    CROP_PROFILES,
    CROP_TO_DATASET_MAP,
    get_crop_profile,
    get_model_crop
)

# DELETE the old CROP_PROFILES dict from crop_service.py
warnings.filterwarnings("ignore")

# PATHS
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
# FIXED — works on Windows too
DATA_PATH    = os.path.join(BASE_DIR, "..", "data", "soil", "Plant_Parameters.csv")
MODEL_PATH   = os.path.join(BASE_DIR, "..", "models", "crop_suitability_model.pkl")
ENCODER_PATH = os.path.join(BASE_DIR, "..", "models", "crop_label_encoder.pkl")


# MICRONUTRIENT DEFICIENCY DATA
# From your 650-row district dataset
# Zn, Fe, Cu, Mn, B, S deficiency %

MICRONUTRIENT_DATA = {
    "Anantapur":     {"Zn": 67.67, "Fe": 65.14, "Cu": 91.88, "Mn": 77.70, "B": 73.54, "S": 85.90},
    "Chittoor":      {"Zn": 80.51, "Fe": 78.19, "Cu": 99.77, "Mn": 91.82, "B": 89.04, "S": 88.62},
    "East Godavari": {"Zn": 79.27, "Fe": 88.14, "Cu": 95.54, "Mn": 97.24, "B": 88.05, "S": 95.67},
    "Guntur":        {"Zn": 58.30, "Fe": 71.16, "Cu": 98.86, "Mn": 91.40, "B": 86.15, "S": 86.81},
    "Krishna":       {"Zn": 78.62, "Fe": 82.02, "Cu": 98.05, "Mn": 95.23, "B": 65.78, "S": 98.56},
    "Kurnool":       {"Zn": 60.70, "Fe": 48.45, "Cu": 97.47, "Mn": 91.34, "B": 92.75, "S": 96.05},
    "Prakasam":      {"Zn": 40.66, "Fe": 59.14, "Cu": 94.65, "Mn": 82.17, "B": 73.99, "S": 69.54},
    "Nellore":       {"Zn": 39.58, "Fe": 55.37, "Cu": 80.72, "Mn": 79.83, "B": 77.23, "S": 87.61},
    "Srikakulam":    {"Zn": 81.05, "Fe": 75.77, "Cu": 98.85, "Mn": 91.31, "B": 96.76, "S": 94.45},
    "Visakhapatnam": {"Zn": 58.75, "Fe": 64.93, "Cu": 96.44, "Mn": 78.35, "B": 85.40, "S": 88.29},
    "Vizianagaram":  {"Zn": 61.60, "Fe": 93.71, "Cu": 95.22, "Mn": 98.34, "B": 79.43, "S": 87.59},
    "West Godavari": {"Zn": 67.36, "Fe": 87.69, "Cu": 96.54, "Mn": 96.76, "B": 87.74, "S": 88.24},
    "Y.S.R.":        {"Zn": 68.61, "Fe": 67.42, "Cu": 92.82, "Mn": 92.72, "B": 71.80, "S": 86.46},
}

NUTRIENT_NAMES = {"Zn": "Zinc", "Fe": "Iron", "Cu": "Copper",
                  "Mn": "Manganese", "B": "Boron", "S": "Sulphur"}

NUTRIENT_FIXES = {
    "Zn": "Apply Zinc Sulphate @ 25 kg/ha before sowing.",
    "Fe": "Apply Ferrous Sulphate @ 25 kg/ha or foliar spray.",
    "Cu": "Apply Copper Sulphate @ 5 kg/ha to soil.",
    "Mn": "Apply Manganese Sulphate @ 10 kg/ha to soil.",
    "B":  "Apply Borax @ 10 kg/ha before sowing.",
    "S":  "Apply Gypsum @ 200-400 kg/ha to soil."
}

DEFICIENCY_THRESHOLD = 70.0



# TRAIN MODEL

def train_crop_model() -> bool:
    print("Training crop suitability model...")

    if not os.path.exists(DATA_PATH):
        print(f"❌ Dataset not found: {DATA_PATH}")
        return False

    df           = pd.read_csv(DATA_PATH)
    df.columns   = df.columns.str.strip()
    feature_cols = ["pH", "Soil EC", "Phosphorus", "Potassium",
                    "Urea", "T.S.P", "M.O.P", "Moisture", "Temperature"]

    X         = df[feature_cols]
    y         = df["Plant Type"]
    encoder   = LabelEncoder()
    y_encoded = encoder.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )

    clf = RandomForestClassifier(
        n_estimators=200, max_depth=20,
        random_state=42,  n_jobs=-1
    )
    clf.fit(X_train, y_train)

    accuracy = accuracy_score(y_test, clf.predict(X_test))
    print(f"✅ Accuracy : {accuracy * 100:.2f}%")
    print(f"   Classes  : {list(encoder.classes_)}")

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    with open(MODEL_PATH,   "wb") as f: pickle.dump(clf,     f)
    with open(ENCODER_PATH, "wb") as f: pickle.dump(encoder, f)
    print(f"✅ Model saved → {MODEL_PATH}")
    return True



# LOAD MODEL AT STARTUP

def _load_model():
    if not os.path.exists(MODEL_PATH):
        print("⚠️  Crop model not found. Training now...")
        if not train_crop_model():
            return None, None
    with open(MODEL_PATH,   "rb") as f: clf     = pickle.load(f)
    with open(ENCODER_PATH, "rb") as f: encoder = pickle.load(f)
    print("✅ Crop suitability model loaded")
    return clf, encoder

clf, encoder = _load_model()



# FUNCTION 1 — CROP SUITABILITY

def check_crop_suitability(
    crop: str, ph: float, soil_ec: float,
    phosphorus: float, potassium: float,
    urea: float, tsp: float, mop: float,
    moisture: float, temperature: float
) -> dict:

    if clf is None:
        return {"error": "Crop model unavailable. Check Plant_Parameters.csv"}

    features = pd.DataFrame([[ph, soil_ec, phosphorus, potassium,
                               urea, tsp, mop, moisture, temperature]],
                             columns=["pH", "Soil EC", "Phosphorus", "Potassium",
                                      "Urea", "T.S.P", "M.O.P", "Moisture", "Temperature"])

    # ── Map farmer's crop to nearest ML model crop ──
    # ML model only knows 10 crops from dataset
    # get_model_crop() maps any of 78 crops to nearest equivalent
    crop_for_model = get_model_crop(crop)

    # ── Get model's prediction using mapped crop ──
    probabilities = clf.predict_proba(features)[0]
    top3_indices  = np.argsort(probabilities)[::-1][:3]
    top3_crops    = encoder.inverse_transform(top3_indices)
    top3_probs    = probabilities[top3_indices]

    # ── Check suitability against MAPPED crop (not original) ──
    # Example: Onion → mapped to Carrots for model check
    mapped_lower  = crop_for_model.strip().lower()
    top3_lower    = [c.lower() for c in top3_crops]
    is_suitable   = mapped_lower in top3_lower
    best_crop     = top3_crops[0].title()

    # ── Calculate confidence ──
    if mapped_lower in top3_lower:
        idx               = top3_lower.index(mapped_lower)
        confidence        = round(float(top3_probs[idx]) * 100, 1)
        suitability_score = min(100, int(confidence * 1.1))
    else:
        confidence        = round(float(top3_probs[0]) * 100, 1)
        suitability_score = max(10, int(confidence * 0.25))

    # ── Plain language reason ──
    # Always show ORIGINAL crop name to farmer (not mapped name)
    if is_suitable and confidence > 60:
        reason = (f"Soil conditions are well suited for {crop.title()}. "
                  f"pH {ph}, Moisture {moisture}%, match {crop.title()} requirements.")
    elif is_suitable:
        reason = (f"Marginally suitable for {crop.title()}. "
                  f"Consider adjusting fertilizer for better yield.")
    else:
        reason = (f"Conditions better suited for {best_crop} than {crop.title()}. "
                  f"pH {ph} and EC {soil_ec} may limit {crop.title()} yield.")

    return {
        "crop":              crop.title(),           # original crop name
        "model_crop_used":   crop_for_model,         # mapped crop (for transparency)
        "is_suitable":       is_suitable,
        "suitability_score": suitability_score,
        "confidence":        confidence,
        "recommended_crop":  best_crop,
        "top_3_crops":       [c.title() for c in top3_crops],
        "top_3_confidence":  [round(float(p) * 100, 1) for p in top3_probs],
        "reason":            reason
    }


# FUNCTION 2 — MICRONUTRIENT WARNINGS

def get_micronutrient_warnings(district: str) -> dict:
    district_title = district.strip().title()
    data           = MICRONUTRIENT_DATA.get(district_title)

    if not data:
        for key in MICRONUTRIENT_DATA:
            if district_title.lower() in key.lower():
                data           = MICRONUTRIENT_DATA[key]
                district_title = key
                break

    if not data:
        return {
            "district": district_title, "warnings": [],
            "summary":  f"No micronutrient data for {district_title}.",
            "available": False
        }

    warnings_list = []
    for nutrient, pct in data.items():
        if pct >= DEFICIENCY_THRESHOLD:
            severity = "High" if pct >= 85 else "Medium"
            warnings_list.append({
                "nutrient":       NUTRIENT_NAMES[nutrient],
                "deficiency_pct": pct,
                "severity":       severity,
                "fix":            NUTRIENT_FIXES[nutrient]
            })

    warnings_list.sort(key=lambda x: (
        -{"High": 2, "Medium": 1}.get(x["severity"], 0),
        -x["deficiency_pct"]
    ))

    if warnings_list:
        top     = warnings_list[0]
        summary = (f"⚠️ {len(warnings_list)} micronutrient deficiencies in "
                   f"{district_title}. Most critical: {top['nutrient']} "
                   f"({top['deficiency_pct']}% farms deficient).")
    else:
        summary = f"✅ No critical micronutrient deficiencies in {district_title}."

    return {
        "district":  district_title,
        "warnings":  warnings_list,
        "summary":   summary,
        "available": True
    }



# FUNCTION 3 — SPOILAGE RISK

def get_spoilage_risk(
    crop: str, storage_type: str,
    transit_hours: float, temperature: float,
    humidity: float, spoilage_factor: float = 1.0
) -> dict:

    crop_title     = crop.strip().title()
    profile = get_crop_profile(crop_title)
    shelf_life     = profile["shelf_life_days"]

    storage_scores = {"cold_storage": 0.1, "cool_storage": 0.3,
                      "basic_shed": 0.6,   "open_air": 1.0}
    storage_penalty  = storage_scores.get(storage_type.lower(), 0.6)
    temp_penalty     = min(1.0, max(0, temperature - profile["ideal_temp"]) / 20.0)
    humidity_penalty = min(1.0, max(0, humidity - profile["ideal_humidity"]) / 40.0)
    transit_penalty  = min(1.0, (transit_hours / 24.0) / max(1, shelf_life * 0.3))

    raw_score  = (storage_penalty * 0.35 + temp_penalty * 0.25 +
                  humidity_penalty * 0.20 + transit_penalty * 0.20) * spoilage_factor
    risk_score = min(100, int(raw_score * 100))
    days_safe  = max(1, int(shelf_life * max(0.1, 1.0 - raw_score)))

    if risk_score >= 65:   risk_level = "High"
    elif risk_score >= 35: risk_level = "Medium"
    else:                  risk_level = "Low"

    actions = _get_preservation_actions(
        crop_title, risk_level, storage_type,
        temperature, humidity, days_safe
    )

    if risk_level == "High":
        summary = f"⚠️ High spoilage risk. Safe for only {days_safe} day(s). Act immediately."
    elif risk_level == "Medium":
        summary = f"⚡ Moderate spoilage risk. Safe for {days_safe} day(s). Improve storage."
    else:
        summary = f"✅ Low spoilage risk. Safe for {days_safe} day(s). Conditions acceptable."

    return {
        "crop":          crop_title,
        "risk_level":    risk_level,
        "risk_score":    risk_score,
        "days_safe":     days_safe,
        "storage_type":  storage_type,
        "actions":       actions,
        "summary":       summary,
        "storage_tip":   profile["storage_tip"],
        "spoilage_note": profile["spoilage_notes"]
    }


def _get_preservation_actions(crop, risk_level, storage_type,
                               temp, humidity, days_safe) -> list:
    actions = [{
        "action":      "Sort and remove damaged produce",
        "cost":        "Free",
        "impact":      "High",
        "description": "Remove bruised/damaged items immediately to prevent spread."
    }]
    if temp > 30:
        actions.append({"action": "Move to shaded area", "cost": "Free",
                        "impact": "Medium",
                        "description": "Shade reduces temperature by 5-8°C."})
    if humidity > 75:
        actions.append({"action": "Improve ventilation", "cost": "Free",
                        "impact": "Medium",
                        "description": "Open vents to reduce humidity buildup."})
    if storage_type in ["open_air", "basic_shed"]:
        actions.append({"action": "Use gunny/jute sacks", "cost": "₹5-10 per bag",
                        "impact": "Medium",
                        "description": "Natural fiber bags allow breathability."})
    if risk_level in ["Medium", "High"]:
        actions.append({"action": "Evaporative cooling (wet cloth/clay pot)",
                        "cost": "₹50-100", "impact": "High",
                        "description": "Reduces temperature by 10-15°C."})
        actions.append({"action": "Move to cool storage facility",
                        "cost": "₹200-500", "impact": "Very High",
                        "description": f"Extends {crop} shelf life by {days_safe * 3} days."})
    if risk_level == "High":
        actions.append({"action": "Sell immediately at nearest market",
                        "cost": "Transport cost only", "impact": "Very High",
                        "description": "High risk — immediate sale prevents total loss."})
    return actions



# FUNCTION 4 — MASTER FUNCTION
# Called by recommend.py route

def get_crop_insight(
    crop: str, district: str,
    ph: float, soil_ec: float,
    phosphorus: float, potassium: float,
    urea: float, tsp: float, mop: float,
    moisture: float, temperature: float,
    storage_type: str = "basic_shed",
    transit_hours: float = 6.0,
    spoilage_factor: float = 1.0
) -> dict:

    return {
        "suitability":   check_crop_suitability(
            crop, ph, soil_ec, phosphorus, potassium,
            urea, tsp, mop, moisture, temperature
        ),
        "micronutrient": get_micronutrient_warnings(district),
        "spoilage":      get_spoilage_risk(
            crop, storage_type, transit_hours,
            temperature, moisture, spoilage_factor
        )
    }



# QUICK TEST — python crop_service.py

if __name__ == "__main__":
    print("\n" + "=" * 55)
    print("  AgriChain — Crop Service Test")
    print("=" * 55)

    result = get_crop_insight(
        crop="Tomato",      district="Guntur",
        ph=6.5,             soil_ec=0.6,
        phosphorus=20.0,    potassium=150.0,
        urea=50.0,          tsp=22.0,
        mop=30.0,           moisture=68.0,
        temperature=72.0,   storage_type="basic_shed",
        transit_hours=8.0
    )

    s  = result["suitability"]
    m  = result["micronutrient"]
    sp = result["spoilage"]

    print("\n── Crop Suitability ──")
    print(f"  Crop              : {s['crop']}")
    print(f"  Is Suitable       : {s['is_suitable']}")
    print(f"  Suitability Score : {s['suitability_score']}/100")
    print(f"  Confidence        : {s['confidence']}%")
    print(f"  Top 3 Crops       : {s['top_3_crops']}")
    print(f"  Reason            : {s['reason']}")

    print("\n── Micronutrient Warnings ──")
    print(f"  District : {m['district']}")
    print(f"  Summary  : {m['summary']}")
    for w in m.get("warnings", []):
        print(f"  [{w['severity']}] {w['nutrient']}: {w['deficiency_pct']}% deficient")
        print(f"  Fix: {w['fix']}")

    print("\n── Spoilage Risk ──")
    print(f"  Risk Level  : {sp['risk_level']}")
    print(f"  Risk Score  : {sp['risk_score']}/100")
    print(f"  Days Safe   : {sp['days_safe']} days")
    print(f"  Summary     : {sp['summary']}")

    print("\n── Preservation Actions ──")
    for i, a in enumerate(sp["actions"], 1):
        print(f"  {i}. [{a['cost']}] {a['action']}")