import requests
from config import API_KEY

CURRENT_WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"

def build_params(city):
    return {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

def get_current_weather(city):
    response = requests.get(CURRENT_WEATHER_URL, params=build_params(city))

    if response.status_code == 200:
        return response.json()
    
    return None

def get_forecast(city):
    response = requests.get(FORECAST_URL, params=build_params(city))

    if response.status_code == 200:
        return response.json()
    
    return None