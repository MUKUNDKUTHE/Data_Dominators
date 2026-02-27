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
# FUNCTION 5 — ARRIVAL SURGE PREDICTION
# Uses historical weekly arrival volume to warn
# farmers when competing supply will flood market
# ─────────────────────────────────────────
def get_arrival_surge_prediction(
    commodity: str,
    state:     str,
    target_date: str = None
) -> dict:
    """
    Predicts weeks with historically high arrival volume for a crop+state.
    Returns alert if the next few weeks are surge weeks → price crash risk.
    """
    commodity = commodity.strip().title()
    state     = state.strip().title()

    filtered = df_mandi[
        (df_mandi["Commodity"] == commodity) &
        (df_mandi["State"]     == state)
    ].copy()

    if len(filtered) < 50:
        return {
            "has_prediction": False,
            "commodity": commodity,
            "state": state,
            "alert": f"Not enough historical data for {commodity} in {state}",
            "advice": "no_data",
            "upcoming_surges": [],
            "best_price_weeks": []
        }

    filtered["week_of_year"] = filtered["Arrival_Date"].dt.isocalendar().week.astype(int)

    weekly = (
        filtered.groupby("week_of_year")
        .agg(arrival_count=("Arrival_Date", "count"), avg_price=("Modal_Price", "mean"))
        .reset_index()
    )

    overall_avg     = weekly["arrival_count"].mean()
    surge_threshold = overall_avg * 1.5
    normal_price    = weekly["avg_price"].mean()

    # Current week
    try:
        target_dt = pd.to_datetime(target_date) if target_date else pd.Timestamp.now()
    except Exception:
        target_dt = pd.Timestamp.now()
    current_week = int(target_dt.isocalendar()[1])

    # Upcoming 4 weeks — check for surges
    upcoming_surges = []
    for delta in range(0, 5):
        w     = ((current_week + delta - 1) % 52) + 1
        match = weekly[weekly["week_of_year"] == w]
        if not match.empty:
            row = match.iloc[0]
            if row["arrival_count"] >= surge_threshold:
                price_drop = round(((row["avg_price"] - normal_price) / normal_price) * 100, 1)
                upcoming_surges.append({
                    "week":             w,
                    "weeks_from_now":   delta,
                    "arrival_index":    round(row["arrival_count"] / overall_avg, 2),
                    "avg_price":        round(row["avg_price"], 0),
                    "price_impact_pct": price_drop
                })

    # Historical top-5 surge weeks (for chart)
    surge_rows = weekly[weekly["arrival_count"] >= surge_threshold].nlargest(5, "arrival_count")
    historical_surges = []
    for _, row in surge_rows.iterrows():
        price_drop = round(((row["avg_price"] - normal_price) / normal_price) * 100, 1)
        historical_surges.append({
            "week":             int(row["week_of_year"]),
            "arrival_index":    round(row["arrival_count"] / overall_avg, 2),
            "avg_price":        round(row["avg_price"], 0),
            "price_impact_pct": price_drop
        })

    # Best weeks to sell (high price, low arrivals)
    best_weeks = weekly.nlargest(3, "avg_price")["week_of_year"].tolist()

    if upcoming_surges:
        ns = upcoming_surges[0]
        if ns["weeks_from_now"] == 0:
            alert  = (f"⚠️ THIS WEEK is historically a high-arrival surge week for {commodity} in {state}. "
                      f"Price is {abs(ns['price_impact_pct'])}% {'below' if ns['price_impact_pct'] < 0 else 'near'} average. "
                      f"Consider selling NOW before further drop or wait until surge passes.")
            advice = "sell_now_or_delay"
        else:
            alert  = (f"⚠️ Arrival surge expected in {ns['weeks_from_now']} week(s) (week {ns['week']}) "
                      f"for {commodity} in {state}. Prices historically "
                      f"{abs(ns['price_impact_pct'])}% {'lower' if ns['price_impact_pct'] < 0 else 'normal'} then. "
                      f"Sell BEFORE the surge for better price.")
            advice = "sell_before_surge"
    else:
        alert  = (f"✅ No arrival surge in the next 4 weeks for {commodity} in {state}. "
                  f"You are in a safe selling window.")
        advice = "good_window"

    return {
        "has_prediction":      True,
        "commodity":           commodity,
        "state":               state,
        "current_week":        current_week,
        "normal_avg_price":    round(normal_price, 0),
        "alert":               alert,
        "advice":              advice,
        "upcoming_surges":     upcoming_surges,
        "historical_surges":   historical_surges,
        "best_price_weeks":    [int(w) for w in best_weeks]
    }


# ─────────────────────────────────────────
# FUNCTION 6 — MIDDLEMAN BYPASS SCORE
# Tells farmer when it makes financial sense
# to sell directly and skip the Arthiya
# ─────────────────────────────────────────
def get_bypass_score(
    crop:              str,
    state:             str,
    quantity_quintals: float,
    predicted_price:   float,
    price_trend:       str = "stable"
) -> dict:
    score   = 0
    reasons = []

    # ── Quantity ──
    if quantity_quintals >= 20:
        score += 3
        reasons.append({"positive": True,  "text": f"Your {quantity_quintals} qtl meets direct buyer minimum (20 qtl)"})
    elif quantity_quintals >= 10:
        score += 2
        reasons.append({"positive": True,  "text": f"Your {quantity_quintals} qtl qualifies for most direct buyers (min 10 qtl)"})
    elif quantity_quintals >= 5:
        score += 1
        reasons.append({"positive": True,  "text": f"{quantity_quintals} qtl may qualify for some direct buyers"})
    else:
        reasons.append({"positive": False, "text": f"Only {quantity_quintals} qtl — too small for direct deals (need 10+ qtl)"})

    # ── Price trend ──
    if price_trend == "rising":
        score += 2
        reasons.append({"positive": True, "text": "Rising prices strengthen your negotiating position"})
    elif price_trend == "falling":
        score += 1
        reasons.append({"positive": True, "text": "Falling prices mean broker's 8% cut hurts more — bypass saves more now"})
    else:
        score += 1
        reasons.append({"positive": True, "text": "Stable prices make direct deal planning straightforward"})

    # ── Commission savings ──
    commission_rate  = 0.08
    commission_saved = round(quantity_quintals * predicted_price * commission_rate, 0)
    if commission_saved > 5000:
        score += 3
        reasons.append({"positive": True, "text": f"Savings of ₹{commission_saved:,.0f} by skipping 8% broker commission"})
    elif commission_saved > 2000:
        score += 2
        reasons.append({"positive": True, "text": f"Savings of ₹{commission_saved:,.0f} by skipping broker commission"})
    else:
        score += 1
        reasons.append({"positive": True, "text": f"Savings of ₹{commission_saved:,.0f} by going direct"})

    # ── State has direct buyer networks ──
    large_apmc = ["maharashtra", "gujarat", "punjab", "haryana",
                  "andhra pradesh", "telangana", "karnataka", "uttar pradesh"]
    if state.lower() in large_apmc:
        score += 2
        reasons.append({"positive": True, "text": f"{state} has established FPO/direct agri-buyer networks"})
    else:
        reasons.append({"positive": False, "text": "Direct buyer network less developed in this state"})

    score = min(score, 10)

    if score >= 8:
        verdict   = "Highly Recommended"
        color     = "green"
        next_step = "Contact your nearest FPO (Farmer Producer Organisation) or APMC direct procurement desk"
    elif score >= 5:
        verdict   = "Worth Trying"
        color     = "yellow"
        next_step = "Search 'FPO {state}' or call Kisan Call Centre 1800-180-1551 for direct buyer referrals".format(state=state)
    else:
        verdict   = "Build Quantity First"
        color     = "red"
        next_step = "Combine with 2-3 neighbouring farmers to reach 10+ qtl, then try direct selling"

    return {
        "bypass_score":       score,
        "max_score":          10,
        "verdict":            verdict,
        "color":              color,
        "commission_saved":   commission_saved,
        "commission_rate_pct": commission_rate * 100,
        "reasons":            reasons,
        "next_step":          next_step
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