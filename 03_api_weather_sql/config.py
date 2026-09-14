import os
from dotenv import load_dotenv

# Charge le contenu de .env dans les variables d'environnement
load_dotenv()

# --- Configuration base de données ---
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5433")
DB_NAME = os.getenv("DB_NAME", "weather_db")
DB_USER = os.getenv("DB_USER", "weather_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "weather_pass")

# On construit une URL de connexion au format standard
# dialecte+driver://user:password@host:port/database
DATABASE_URL = (
    f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# --- Les villes qu'on veut surveiller ---
DESTINATIONS = [
    {"city": "Abidjan", "country": "CI"},
    {"city": "Paris", "country": "FR"},
    {"city": "Marrakech", "country": "MA"},
    {"city": "Tokyo", "country": "JP"},
    {"city": "New York", "country": "US"},
    {"city": "Dakar", "country": "SN"},
    {"city": "Barcelone", "country": "ES"},
    {"city": "Dubaï", "country": "AE"},
    {"city": "Rio de Janeiro", "country": "BR"},
    {"city": "Le Cap", "country": "ZA"},
]