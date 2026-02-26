# backend/services/weather_service.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()


# CONFIG
# Free tier: 60 calls/min, no credit card needed
# Uses Current Weather API (free) + 5-day Forecast API (free)

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL_CURRENT    = "https://api.openweathermap.org/data/2.5/weather"
BASE_URL_FORECAST   = "https://api.openweathermap.org/data/2.5/forecast"
BASE_URL_GEO        = "http://api.openweathermap.org/geo/1.0/direct"


# INDIA STATE → COORDINATES MAP
# Fallback if geocoding fails
# Covers all major mandi states

STATE_COORDINATES = {
    "Andhra Pradesh":       {"lat": 15.9129,  "lon": 79.7400},
    "Arunachal Pradesh":    {"lat": 28.2180,  "lon": 94.7278},
    "Assam":                {"lat": 26.2006,  "lon": 92.9376},
    "Bihar":                {"lat": 25.0961,  "lon": 85.3131},
    "Chhattisgarh":         {"lat": 21.2787,  "lon": 81.8661},
    "Delhi":                {"lat": 28.7041,  "lon": 77.1025},
    "Goa":                  {"lat": 15.2993,  "lon": 74.1240},
    "Gujarat":              {"lat": 22.2587,  "lon": 71.1924},
    "Haryana":              {"lat": 29.0588,  "lon": 76.0856},
    "Himachal Pradesh":     {"lat": 31.1048,  "lon": 77.1734},
    "Jammu And Kashmir":    {"lat": 33.7782,  "lon": 76.5762},
    "Jharkhand":            {"lat": 23.6102,  "lon": 85.2799},
    "Karnataka":            {"lat": 15.3173,  "lon": 75.7139},
    "Kerala":               {"lat": 10.8505,  "lon": 76.2711},
    "Madhya Pradesh":       {"lat": 22.9734,  "lon": 78.6569},
    "Maharashtra":          {"lat": 19.7515,  "lon": 75.7139},
    "Manipur":              {"lat": 24.6637,  "lon": 93.9063},
    "Meghalaya":            {"lat": 25.4670,  "lon": 91.3662},
    "Mizoram":              {"lat": 23.1645,  "lon": 92.9376},
    "Nagaland":             {"lat": 26.1584,  "lon": 94.5624},
    "Odisha":               {"lat": 20.9517,  "lon": 85.0985},
    "Punjab":               {"lat": 31.1471,  "lon": 75.3412},
    "Rajasthan":            {"lat": 27.0238,  "lon": 74.2179},
    "Sikkim":               {"lat": 27.5330,  "lon": 88.5122},
    "Tamil Nadu":           {"lat": 11.1271,  "lon": 78.6569},
    "Telangana":            {"lat": 18.1124,  "lon": 79.0193},
    "Tripura":              {"lat": 23.9408,  "lon": 91.9882},
    "Uttar Pradesh":        {"lat": 26.8467,  "lon": 80.9462},
    "Uttarakhand":          {"lat": 30.0668,  "lon": 79.0193},
    "West Bengal":          {"lat": 22.9868,  "lon": 87.8550},
}



# HELPER — GET COORDINATES
# Tries geocoding first, falls back to state map

def get_coordinates(city: str, state: str) -> dict:
    """
    Gets lat/lon for a city+state combination.
    Tries OpenWeather geocoding first, falls back to state center.
    """
    try:
        response = requests.get(
            BASE_URL_GEO,
            params={
                "q":     f"{city},{state},IN",
                "limit": 1,
                "appid": OPENWEATHER_API_KEY
            },
            timeout=5
        )
        data = response.json()
        if data and len(data) > 0:
            return {"lat": data[0]["lat"], "lon": data[0]["lon"]}
    except Exception:
        pass

    # Fallback to state coordinates
    state_title = state.strip().title()
    if state_title in STATE_COORDINATES:
        return STATE_COORDINATES[state_title]

    # Final fallback — center of India
    return {"lat": 20.5937, "lon": 78.9629}



# HELPER — INTERPRET WEATHER FOR FARMING
# Converts raw weather data into farming signals

def interpret_weather(temp: float, humidity: float,
                      rainfall: float, wind_speed: float) -> dict:
    """
    Converts raw weather numbers into farming-relevant signals.

    Returns:
        harvest_risk    : Low / Medium / High
        transit_risk    : Low / Medium / High
        spoilage_factor : multiplier for spoilage calculation (1.0 = normal)
        summary         : plain language weather summary
    """

    issues = []

    # Temperature analysis
    if temp > 38:
        temp_risk = "High"
        issues.append("extreme heat")
    elif temp > 32:
        temp_risk = "Medium"
        issues.append("high temperature")
    else:
        temp_risk = "Low"

    # Humidity analysis
    if humidity > 85:
        humidity_risk = "High"
        issues.append("very high humidity")
    elif humidity > 70:
        humidity_risk = "Medium"
        issues.append("moderate humidity")
    else:
        humidity_risk = "Low"

    # Rainfall analysis
    if rainfall > 10:
        rainfall_risk = "High"
        issues.append("heavy rainfall")
    elif rainfall > 2:
        rainfall_risk = "Medium"
        issues.append("moderate rainfall")
    else:
        rainfall_risk = "Low"

    # Wind analysis
    if wind_speed > 10:
        wind_risk = "Medium"
        issues.append("strong winds")
    else:
        wind_risk = "Low"

    # Overall harvest risk
    risk_scores = {
        "Low": 1, "Medium": 2, "High": 3
    }
    avg_risk = (
        risk_scores[temp_risk] +
        risk_scores[humidity_risk] +
        risk_scores[rainfall_risk]
    ) / 3

    if avg_risk >= 2.5:
        harvest_risk = "High"
        transit_risk = "High"
    elif avg_risk >= 1.5:
        harvest_risk = "Medium"
        transit_risk = "Medium"
    else:
        harvest_risk = "Low"
        transit_risk = "Low"

    # Spoilage factor — multiplier used by spoilage_service
    # High heat + humidity = faster spoilage
    spoilage_factor = round(1.0 + (avg_risk - 1) * 0.3, 2)

    # Plain language summary
    if issues:
        summary = f"Weather concern: {', '.join(issues)}. " \
                  f"Harvest risk is {harvest_risk.lower()}."
    else:
        summary = f"Weather conditions are favorable. " \
                  f"Good time to harvest and transport."

    return {
        "harvest_risk":    harvest_risk,
        "transit_risk":    transit_risk,
        "spoilage_factor": spoilage_factor,
        "summary":         summary,
        "issues":          issues
    }



# FUNCTION 1 — GET CURRENT WEATHER
# Returns current conditions for a location

def get_current_weather(city: str, state: str) -> dict:
    """
    Gets current weather for a city/state in India.

    Returns:
        temperature, humidity, rainfall, wind_speed,
        weather_description, farming signals
    """

    if not OPENWEATHER_API_KEY:
        return _mock_weather(city, state)

    coords = get_coordinates(city, state)

    try:
        response = requests.get(
            BASE_URL_CURRENT,
            params={
                "lat":   coords["lat"],
                "lon":   coords["lon"],
                "appid": OPENWEATHER_API_KEY,
                "units": "metric"
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        temp        = data["main"]["temp"]
        humidity    = data["main"]["humidity"]
        wind_speed  = data["wind"]["speed"]
        description = data["weather"][0]["description"]
        rainfall    = data.get("rain", {}).get("1h", 0)

        signals = interpret_weather(temp, humidity, rainfall, wind_speed)

        return {
            "city":               city.title(),
            "state":              state.title(),
            "temperature":        round(temp, 1),
            "humidity":           humidity,
            "rainfall_mm":        rainfall,
            "wind_speed_ms":      round(wind_speed, 1),
            "description":        description,
            "harvest_risk":       signals["harvest_risk"],
            "transit_risk":       signals["transit_risk"],
            "spoilage_factor":    signals["spoilage_factor"],
            "weather_summary":    signals["summary"],
            "source":             "live"
        }

    except requests.exceptions.RequestException as e:
        print(f"⚠️ OpenWeather API error: {e}. Using mock data.")
        return _mock_weather(city, state)



# FUNCTION 2 — GET 5-DAY FORECAST SUMMARY
# Returns weather outlook for harvest planning

def get_weather_forecast(city: str, state: str, days: int = 5) -> dict:
    """
    Gets 5-day weather forecast summary for harvest window planning.

    Returns:
        daily forecast with farming risk per day
    """

    if not OPENWEATHER_API_KEY:
        return _mock_forecast(city, state)

    coords = get_coordinates(city, state)

    try:
        response = requests.get(
            BASE_URL_FORECAST,
            params={
                "lat":   coords["lat"],
                "lon":   coords["lon"],
                "appid": OPENWEATHER_API_KEY,
                "units": "metric",
                "cnt":   days * 8   # 8 readings per day (every 3hrs)
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        # Group by day and average
        daily = {}
        for item in data["list"]:
            date = item["dt_txt"].split(" ")[0]
            if date not in daily:
                daily[date] = {
                    "temps": [], "humidity": [],
                    "rainfall": [], "wind": []
                }
            daily[date]["temps"].append(item["main"]["temp"])
            daily[date]["humidity"].append(item["main"]["humidity"])
            daily[date]["rainfall"].append(item.get("rain", {}).get("3h", 0))
            daily[date]["wind"].append(item["wind"]["speed"])

        forecast_days = []
        for date, values in list(daily.items())[:days]:
            avg_temp     = round(sum(values["temps"]) / len(values["temps"]), 1)
            avg_humidity = round(sum(values["humidity"]) / len(values["humidity"]), 1)
            total_rain   = round(sum(values["rainfall"]), 1)
            avg_wind     = round(sum(values["wind"]) / len(values["wind"]), 1)

            signals = interpret_weather(avg_temp, avg_humidity,
                                        total_rain, avg_wind)

            forecast_days.append({
                "date":           date,
                "temperature":    avg_temp,
                "humidity":       avg_humidity,
                "rainfall_mm":    total_rain,
                "harvest_risk":   signals["harvest_risk"],
                "transit_risk":   signals["transit_risk"],
                "summary":        signals["summary"]
            })

        # Find best harvest day (lowest risk)
        best_day = min(
            forecast_days,
            key=lambda d: {"Low": 1, "Medium": 2, "High": 3}[d["harvest_risk"]]
        )

        return {
            "city":          city.title(),
            "state":         state.title(),
            "forecast":      forecast_days,
            "best_day":      best_day["date"],
            "best_day_risk": best_day["harvest_risk"],
            "summary":       f"Best day to harvest/transport: {best_day['date']} "
                             f"({best_day['harvest_risk']} risk)",
            "source":        "live"
        }

    except requests.exceptions.RequestException as e:
        print(f"⚠️ OpenWeather forecast error: {e}. Using mock data.")
        return _mock_forecast(city, state)



# FUNCTION 3 — GET FULL WEATHER INSIGHT
# Master function called by recommend route

def get_weather_insight(city: str, state: str) -> dict:
    """
    Master function — combines current weather + forecast.
    Called by recommend.py route.
    """
    current  = get_current_weather(city, state)
    forecast = get_weather_forecast(city, state)

    return {
        "current":  current,
        "forecast": forecast
    }



# MOCK DATA
# Used when API key is missing or API fails
# Ensures demo works even without API key

def _mock_weather(city: str, state: str) -> dict:
    return {
        "city":            city.title(),
        "state":           state.title(),
        "temperature":     28.5,
        "humidity":        65,
        "rainfall_mm":     0,
        "wind_speed_ms":   3.2,
        "description":     "partly cloudy",
        "harvest_risk":    "Low",
        "transit_risk":    "Low",
        "spoilage_factor": 1.0,
        "weather_summary": "Weather conditions are favorable. Good time to harvest and transport.",
        "source":          "mock"
    }


def _mock_forecast(city: str, state: str) -> dict:
    from datetime import datetime, timedelta
    today = datetime.today()
    forecast_days = []
    for i in range(5):
        day = today + timedelta(days=i)
        forecast_days.append({
            "date":         day.strftime("%Y-%m-%d"),
            "temperature":  28 + i,
            "humidity":     60 + i * 2,
            "rainfall_mm":  0,
            "harvest_risk": "Low",
            "transit_risk": "Low",
            "summary":      "Favorable conditions for harvest and transport."
        })
    return {
        "city":          city.title(),
        "state":         state.title(),
        "forecast":      forecast_days,
        "best_day":      today.strftime("%Y-%m-%d"),
        "best_day_risk": "Low",
        "summary":       f"Best day to harvest/transport: {today.strftime('%Y-%m-%d')} (Low risk)",
        "source":        "mock"
    }



# QUICK TEST — python weather_service.py

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  Testing Weather Service")
    print("=" * 50)

    result = get_weather_insight(
        city  = "Pune",
        state = "Maharashtra"
    )

    print("\n── Current Weather ──")
    for k, v in result["current"].items():
        print(f"  {k:<20}: {v}")

    print("\n── 5-Day Forecast ──")
    for day in result["forecast"]["forecast"]:
        print(f"  {day['date']}  Temp: {day['temperature']}°C  "
              f"Rain: {day['rainfall_mm']}mm  "
              f"Risk: {day['harvest_risk']}")

    print(f"\n  Best harvest day: {result['forecast']['best_day']}")
    print(f"  {result['forecast']['summary']}")