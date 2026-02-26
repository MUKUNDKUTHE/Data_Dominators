# backend/models/predict_price.py

import pandas as pd
import os
from catboost import CatBoostRegressor


# LOAD MODEL ONCE AT STARTUP

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "agrichain_price_model.cbm")

model = CatBoostRegressor()
model.load_model(MODEL_PATH)
print(f"✅ Price model loaded from {MODEL_PATH}")


# HELPERS

def get_season(month: int) -> str:
    if month in [12, 1, 2]:      return "winter"
    if month in [3, 4, 5]:       return "summer"
    if month in [6, 7, 8, 9]:    return "monsoon"
    return "post_monsoon"


def predict_price(
    state:        str,
    district:     str,
    market:       str,
    commodity:    str,
    variety:      str,
    grade:        str,
    date:         str,
    price_spread: float = 200.0   # default avg spread if unknown
) -> dict:
    """
    Predicts the Modal Price for a given commodity, location, and date.

    Parameters:
        state        : e.g. "Maharashtra"
        district     : e.g. "Pune"
        market       : e.g. "Pune"
        commodity    : e.g. "Tomato"
        variety      : e.g. "Local"
        grade        : e.g. "Medium"
        date         : e.g. "2025-10-15" or "15-10-2025"
        price_spread : difference between min and max price (optional)

    Returns:
        dict with predicted_price, confidence_range, and input summary
    """

    # Parse date
    parsed_date = pd.to_datetime(date, dayfirst=True, errors="coerce")
    if pd.isna(parsed_date):
        return {"error": f"Invalid date format: {date}. Use YYYY-MM-DD or DD-MM-YYYY"}

    features = {
        "State":        state.strip().title(),
        "District":     district.strip().title(),
        "Market":       market.strip().title(),
        "Commodity":    commodity.strip().title(),
        "Variety":      variety.strip().title(),
        "Grade":        grade.strip().title(),
        "season":       get_season(parsed_date.month),
        "year":         parsed_date.year,
        "month":        parsed_date.month,
        "week":         parsed_date.isocalendar()[1],
        "price_spread": price_spread
    }

    input_df        = pd.DataFrame([features])
    predicted_price = model.predict(input_df)[0]
    predicted_price = max(0, round(predicted_price, 2))

    # Rough confidence range (±10%)
    lower = round(predicted_price * 0.90, 2)
    upper = round(predicted_price * 1.10, 2)

    return {
        "commodity":        commodity.title(),
        "market":           market.title(),
        "state":            state.title(),
        "date":             str(parsed_date.date()),
        "predicted_price":  predicted_price,
        "confidence_range": {"low": lower, "high": upper},
        "unit":             "₹ per quintal",
        "season":           features["season"]
    }



# QUICK TEST — run this file directly
# python predict_price.py

if __name__ == "__main__":
    result = predict_price(
        state     = "Maharashtra",
        district  = "Pune",
        market    = "Pune",
        commodity = "Tomato",
        variety   = "Local",
        grade     = "Medium",
        date      = "2025-10-15"
    )
    print("\n─── Prediction Result ───")
    for key, value in result.items():
        print(f"  {key:<20}: {value}")