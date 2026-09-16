import os
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

# Charge .env pour récupérer la clé API (spécifique à cette source)
load_dotenv()


# Identifiant unique de cette source
SOURCE_NAME = "openweather"

# Configuration spécifique à OpenWeather
API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def fetch(city: str, country: str) -> dict | None:
    """Appelle l'API OpenWeather pour une ville."""
    params = {
        "q": f"{city},{country}",
        "appid": API_KEY,
        "units": "metric",
        "lang": "fr",
    }
    try:
        r = requests.get(BASE_URL, params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.HTTPError as e:
        print(f"Erreur HTTP OpenWeather {city}: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Erreur reseau OpenWeather {city}: {e}")
    return None


def transform(raw: dict) -> dict | None:
    """Transforme une réponse OpenWeather en dict normalisé."""
    if not raw:
        return None
    try:
        return {
            "city": raw["name"],
            "city_code": raw["id"],
            "source": SOURCE_NAME,
            "country": raw["sys"]["country"],
            "latitude": raw["coord"]["lat"],
            "longitude": raw["coord"]["lon"],
            "temperature": raw["main"]["temp"],
            "feels_like":  raw["main"]["feels_like"],
            "temp_min": raw["main"]["temp_min"],
            "temp_max": raw["main"]["temp_max"],
            "humidity": raw["main"]["humidity"],
            "pressure": raw["main"]["pressure"],
            "weather_main": raw["weather"][0]["main"],
            "weather_desc": raw["weather"][0]["description"],
            "wind_speed": raw.get("wind", {}).get("speed"),
            "wind_deg": raw.get("wind", {}).get("deg"),
            "clouds": raw.get("clouds", {}).get("all"),
            "collected_at": datetime.now(timezone.utc),
        }
    except KeyError as e:
        print(f"Champ manquant OpenWeather pour {raw.get('name', '?')}: {e}")
        return None