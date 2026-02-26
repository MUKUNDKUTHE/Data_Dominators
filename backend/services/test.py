# run this from backend/ folder
from dotenv import load_dotenv
load_dotenv()
from weather_service import get_weather

data = get_weather("Wardha")
print(data)