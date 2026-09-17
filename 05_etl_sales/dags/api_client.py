"""
Client pour l'API REST Countries v5.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("RESTCOUNTRIES_API_KEY")
BASE_URL = "https://api.restcountries.com/countries/v5"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}


def fetch_all_countries() -> list[dict]:
    """Récupère les données de tous les pays (3 pages de 100)."""
    all_countries = []

    for offset in (0, 100, 200):
        params = {
            "limit": 100,
            "offset": offset,
        }
        print(f"  Appel API offset={offset}...")
        response = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        countries = data.get("data", {}).get("objects", [])
        if not countries:
            break

        all_countries.extend(countries)
        print(f"    {len(countries)} pays récupérés.")

    print(f"  Total : {len(all_countries)} pays.")
    return all_countries


def parse_countries(raw_countries: list[dict]) -> list[dict]:
    """Normalise les données de l'API.
    
    Ignore les pays sans code ISO valide (évite les chaînes vides
    qui causent des erreurs d'unicité dans Redshift).
    """
    rows = []
    for c in raw_countries:
        # Récupérer le code ISO alpha-2
        code = c.get("codes", {}).get("alpha_2")
        if not code:
            continue

        code = str(code).strip()
        if not code:
            continue

        # Extraire l'aire (parfois dict, parfois nombre)
        area = c.get("area")
        if isinstance(area, dict):
            area = area.get("kilometers")

        rows.append({
            "country_code": code,
            "country_name": c.get("names", {}).get("common"),
            "region":       c.get("region"),
            "subregion":    c.get("subregion"),
            "population":   c.get("population"),
            "area":         area,
        })
    return rows