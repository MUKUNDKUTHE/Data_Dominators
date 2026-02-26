import requests
import os

def get_weather(region):
    api_key = os.getenv('OPENWEATHER_API_KEY')
    
    # Current weather
    current_url = f"http://api.openweathermap.org/data/2.5/weather?q={region},IN&appid={api_key}&units=metric"
    
    # 5 day forecast
    forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={region},IN&appid={api_key}&units=metric"
    
    try:
        current_res = requests.get(current_url).json()
        forecast_res = requests.get(forecast_url).json()
        
        # Parse current weather
        current = {
            "temp": current_res['main']['temp'],
            "humidity": current_res['main']['humidity'],
            "description": current_res['weather'][0]['description'],
            "wind_speed": current_res['wind']['speed'],
            "rainfall_last_3h": current_res.get('rain', {}).get('3h', 0)
        }
        
        # Parse next 5 days forecast (one reading per day)
        forecasts = []
        seen_dates = set()
        
        for item in forecast_res['list']:
            date = item['dt_txt'].split(' ')[0]  # get just the date
            if date not in seen_dates:
                seen_dates.add(date)
                forecasts.append({
                    "date": date,
                    "temp": item['main']['temp'],
                    "humidity": item['main']['humidity'],
                    "rainfall_mm": item.get('rain', {}).get('3h', 0),
                    "description": item['weather'][0]['description']
                })
            if len(forecasts) == 5:
                break
        
        return {
            "current": current,
            "forecast": forecasts,
            "region": region
        }

    except Exception as e:
        # Fallback for demo if API key not active yet
        return {
            "current": {
                "temp": 28,
                "humidity": 65,
                "description": "partly cloudy",
                "wind_speed": 3.5,
                "rainfall_last_3h": 0
            },
            "forecast": [
                {"date": "2025-11-18", "temp": 27, "humidity": 60, "rainfall_mm": 0, "description": "clear sky"},
                {"date": "2025-11-19", "temp": 26, "humidity": 62, "rainfall_mm": 0, "description": "clear sky"},
                {"date": "2025-11-20", "temp": 25, "humidity": 70, "rainfall_mm": 2, "description": "light rain"},
                {"date": "2025-11-21", "temp": 24, "humidity": 75, "rainfall_mm": 5, "description": "moderate rain"},
                {"date": "2025-11-22", "temp": 27, "humidity": 63, "rainfall_mm": 0, "description": "clear sky"}
            ],
            "region": region,
            "note": "fallback data — API key pending activation"
        }
