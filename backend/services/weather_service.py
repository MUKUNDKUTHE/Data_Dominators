import requests
import os

def get_weather(region):
    api_key = os.getenv('WEATHER_API_KEY')
    
    # Current weather
    current_url = f"https://api.weatherapi.com/v1/current.json?key={api_key}&q={region}&aqi=no"
    
    # 5 day forecast (forecast.json gives upto 3 days on free plan)
    forecast_url = f"https://api.weatherapi.com/v1/forecast.json?key={api_key}&q={region}&days=3&aqi=no&alerts=yes"
    
    try:
        current_res = requests.get(current_url).json()
        forecast_res = requests.get(forecast_url).json()
        
        # Parse current weather
        current = {
            "temp": current_res['current']['temp_c'],
            "humidity": current_res['current']['humidity'],
            "description": current_res['current']['condition']['text'],
            "wind_speed": current_res['current']['wind_kph'],
            "rainfall_last_hour": current_res['current'].get('precip_mm', 0),
            "feels_like": current_res['current']['feelslike_c'],
            "uv_index": current_res['current']['uv']
        }
        
        # Parse 3 day forecast
        forecasts = []
        for day in forecast_res['forecast']['forecastday']:
            forecasts.append({
                "date": day['date'],
                "max_temp": day['day']['maxtemp_c'],
                "min_temp": day['day']['mintemp_c'],
                "avg_humidity": day['day']['avghumidity'],
                "total_rainfall_mm": day['day']['totalprecip_mm'],
                "description": day['day']['condition']['text'],
                "rain_chance_percent": day['day']['daily_chance_of_rain']
            })
        
        # Pull weather alerts if any
        alerts = []
        for alert in forecast_res.get('alerts', {}).get('alert', []):
            alerts.append({
                "headline": alert.get('headline'),
                "severity": alert.get('severity'),
                "description": alert.get('desc', '')[:200]  # trim long alerts
            })

        return {
            "current": current,
            "forecast": forecasts,
            "alerts": alerts,
            "region": region
        }

    except Exception as e:
        print(f"Weather API error: {e}")
        # Fallback static data so demo never crashes
        return {
            "current": {
                "temp": 28,
                "humidity": 65,
                "description": "Partly Cloudy",
                "wind_speed": 12,
                "rainfall_last_hour": 0,
                "feels_like": 30,
                "uv_index": 5
            },
            "forecast": [
                {"date": "2025-11-18", "max_temp": 30, "min_temp": 22, "avg_humidity": 60, "total_rainfall_mm": 0, "description": "Sunny", "rain_chance_percent": 5},
                {"date": "2025-11-19", "max_temp": 29, "min_temp": 21, "avg_humidity": 65, "total_rainfall_mm": 2, "description": "Light Rain", "rain_chance_percent": 40},
                {"date": "2025-11-20", "max_temp": 27, "min_temp": 20, "avg_humidity": 75, "total_rainfall_mm": 8, "description": "Moderate Rain", "rain_chance_percent": 75}
            ],
            "alerts": [],
            "region": region,
            "note": "fallback data — check API key"
        }
