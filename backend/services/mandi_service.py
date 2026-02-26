# backend/services/mandi_service.py

import pandas as pd
import numpy as np
import os
from catboost import CatBoostRegressor

# ─────────────────────────────────────────
# LOAD MODEL ONCE AT STARTUP
# ─────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "../models/agrichain_price_model.cbm")

model = CatBoostRegressor()
model.load_model(MODEL_PATH)
print(f"✅ Mandi price model loaded")

# ─────────────────────────────────────────
# LOAD MANDI PRICE DATA
# Used for trend analysis and market comparison
# ─────────────────────────────────────────
DATA_PATH = os.path.join(BASE_DIR, "../data/processed/mandi_prices.csv")

print("Loading mandi price data for trend analysis...")
df_mandi = pd.read_csv(DATA_PATH, parse_dates=["Arrival_Date"])
df_mandi["Commodity"] = df_mandi["Commodity"].str.strip().str.title()
df_mandi["State"]     = df_mandi["State"].str.strip().str.title()
df_mandi["Market"]    = df_mandi["Market"].str.strip().str.title()
print(f"✅ Mandi data loaded: {len(df_mandi):,} rows")


# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────
def get_season(month: int) -> str:
    if month in [12, 1, 2]:   return "winter"
    if month in [3, 4, 5]:    return "summer"
    if month in [6, 7, 8, 9]: return "monsoon"
    return "post_monsoon"


# ─────────────────────────────────────────
# FUNCTION 1 — PREDICT PRICE
# Core prediction for a single input
# ─────────────────────────────────────────
def predict_price(
    state:        str,
    district:     str,
    market:       str,
    commodity:    str,
    variety:      str,
    grade:        str,
    date:         str,
    price_spread: float = 200.0
) -> dict:
    """
    Predicts modal price for a commodity at a specific market and date.

    Returns:
        dict with predicted_price, confidence_range, season
    """

    parsed_date = pd.to_datetime(date, errors="coerce")
    if pd.isna(parsed_date):
        return {"error": f"Invalid date: {date}. Use YYYY-MM-DD or DD-MM-YYYY"}

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
        "week":         int(parsed_date.isocalendar()[1]),
        "price_spread": float(price_spread)
    }

    input_df        = pd.DataFrame([features])
    predicted_price = float(model.predict(input_df)[0])
    predicted_price = round(max(0, predicted_price), 2)

    return {
        "commodity":       commodity.title(),
        "market":          market.title(),
        "state":           state.title(),
        "date":            str(parsed_date.date()),
        "predicted_price": predicted_price,
        "confidence_range": {
            "low":  round(predicted_price * 0.90, 2),
            "high": round(predicted_price * 1.10, 2)
        },
        "unit":   "₹ per quintal",
        "season": features["season"]
    }


# ─────────────────────────────────────────
# FUNCTION 2 — GET PRICE TREND
# Tells farmer if prices are rising or falling
# Looks at last 3 months of historical data
# ─────────────────────────────────────────
def get_price_trend(commodity: str, state: str) -> dict:
    """
    Analyzes recent price trend for a commodity in a state.

    Returns:
        trend direction, percentage change, and plain language summary
    """

    commodity = commodity.strip().title()
    state     = state.strip().title()

    # Filter to this commodity + state
    filtered = df_mandi[
        (df_mandi["Commodity"] == commodity) &
        (df_mandi["State"]     == state)
    ].copy()

    if len(filtered) < 10:
        return {
            "trend":          "unknown",
            "change_pct":     0,
            "summary":        f"Not enough data for {commodity} in {state}",
            "monthly_prices": []
        }

    # Get last 6 months of data
    filtered     = filtered.sort_values("Arrival_Date")
    recent       = filtered[
        filtered["Arrival_Date"] >= filtered["Arrival_Date"].max() - pd.DateOffset(months=6)
    ]

    # Monthly average prices
    recent["month_year"] = recent["Arrival_Date"].dt.to_period("M")
    monthly_avg = (
        recent.groupby("month_year")["Modal_Price"]
        .mean()
        .round(2)
        .reset_index()
    )
    monthly_avg["month_year"] = monthly_avg["month_year"].astype(str)

    if len(monthly_avg) < 2:
        return {
            "trend":          "stable",
            "change_pct":     0,
            "summary":        "Insufficient monthly data for trend",
            "monthly_prices": monthly_avg.to_dict("records")
        }

    # Compare last month vs 3 months ago
    latest_price = monthly_avg["Modal_Price"].iloc[-1]
    older_price  = monthly_avg["Modal_Price"].iloc[0]
    change_pct   = round(((latest_price - older_price) / older_price) * 100, 2)

    if change_pct > 5:
        trend   = "rising"
        summary = f"{commodity} prices in {state} are rising (+{change_pct}% over last 6 months). Good time to sell soon."
    elif change_pct < -5:
        trend   = "falling"
        summary = f"{commodity} prices in {state} are falling ({change_pct}% over last 6 months). Consider selling immediately."
    else:
        trend   = "stable"
        summary = f"{commodity} prices in {state} are stable ({change_pct}% change). Normal market conditions."

    return {
        "trend":          trend,
        "change_pct":     change_pct,
        "summary":        summary,
        "monthly_prices": monthly_avg.to_dict("records")
    }


# ─────────────────────────────────────────
# FUNCTION 3 — GET BEST MARKET
# Finds top 3 markets in a state for a commodity
# Based on historical average modal price
# ─────────────────────────────────────────
def get_best_markets(commodity: str, state: str, top_n: int = 3) -> dict:
    """
    Finds the best markets to sell a commodity in a given state
    based on historical average prices.

    Returns:
        ranked list of markets with average prices
    """

    commodity = commodity.strip().title()
    state     = state.strip().title()

    filtered = df_mandi[
        (df_mandi["Commodity"] == commodity) &
        (df_mandi["State"]     == state)
    ].copy()

    if len(filtered) < 10:
        return {
            "best_market": "Unknown",
            "markets":     [],
            "summary":     f"Not enough data for {commodity} in {state}"
        }

    # Use only last 12 months for relevance
    filtered = filtered[
        filtered["Arrival_Date"] >= filtered["Arrival_Date"].max() - pd.DateOffset(months=12)
    ]

    # Average modal price per market
    market_avg = (
        filtered.groupby("Market")["Modal_Price"]
        .agg(["mean", "count"])
        .reset_index()
        .rename(columns={"mean": "avg_price", "count": "data_points"})
    )

    # Only include markets with enough data points
    market_avg = market_avg[market_avg["data_points"] >= 5]
    market_avg = market_avg.sort_values("avg_price", ascending=False)
    market_avg["avg_price"] = market_avg["avg_price"].round(2)

    top_markets  = market_avg.head(top_n).to_dict("records")
    best_market  = top_markets[0]["Market"] if top_markets else "Unknown"
    best_price   = top_markets[0]["avg_price"] if top_markets else 0

    return {
        "best_market": best_market,
        "best_price":  best_price,
        "markets":     top_markets,
        "summary":     f"Best market for {commodity} in {state} is {best_market} "
                       f"with avg price ₹{best_price}/quintal"
    }


# ─────────────────────────────────────────
# FUNCTION 4 — GET FULL MANDI INSIGHT
# Master function — combines all 3 above
# This is what the API route calls
# ─────────────────────────────────────────
def get_mandi_insight(
    state:     str,
    district:  str,
    market:    str,
    commodity: str,
    variety:   str,
    grade:     str,
    date:      str
) -> dict:
    """
    Master function called by recommend.py route.
    Returns price prediction + trend + best markets in one call.
    """

    price_result  = predict_price(
        state, district, market, commodity, variety, grade, date
    )
    trend_result  = get_price_trend(commodity, state)
    market_result = get_best_markets(commodity, state)

    return {
        "price_prediction": price_result,
        "price_trend":      trend_result,
        "best_markets":     market_result
    }


# ─────────────────────────────────────────
# QUICK TEST — python mandi_service.py
# ─────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  Testing Mandi Service")
    print("=" * 50)

    result = get_mandi_insight(
        state     = "Maharashtra",
        district  = "Pune",
        market    = "Pune",
        commodity = "Tomato",
        variety   = "Local",
        grade     = "Medium",
        date      = "2025-10-15"
    )

    print("\n── Price Prediction ──")
    for k, v in result["price_prediction"].items():
        print(f"  {k:<20}: {v}")

    print("\n── Price Trend ──")
    for k, v in result["price_trend"].items():
        if k != "monthly_prices":
            print(f"  {k:<20}: {v}")

    print("\n── Best Markets ──")
    for k, v in result["best_markets"].items():
        if k != "markets":
            print(f"  {k:<20}: {v}")
    print("\n  Top Markets:")
    for m in result["best_markets"]["markets"]:
        print(f"    {m['Market']:<20} ₹{m['avg_price']}/quintal")