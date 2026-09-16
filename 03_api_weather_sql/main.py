# Point d'entrée du pipeline météo (exécution locale sans Airflow)

import json
import pandas as pd
from datetime import datetime

from config import DESTINATIONS
from sources import openweather
from database import (
    test_connection,
    insert_weather,
    query_latest_weather,
)


# Registre des sources actives
ACTIVE_SOURCES = [
    openweather,
]


# Étape 1 : Extract - appel API, écriture JSON brut
def extract(destinations: list[dict]) -> str:
    print(f"Extract : collecte via {len(ACTIVE_SOURCES)} source(s) pour {len(destinations)} villes...")

    raw_responses = []

    for source_module in ACTIVE_SOURCES:
        print(f"   Source : {source_module.SOURCE_NAME}")

        for dest in destinations:
            city = dest["city"]
            country = dest["country"]

            print(f"      -> {city} ({country})...", end=" ")

            raw = source_module.fetch(city, country)
            if not raw:
                print("ECHEC")
                continue

            raw_responses.append(raw)
            print("OK")

    path = "/tmp/weather_raw.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(raw_responses, f, ensure_ascii=False)

    print(f"   {len(raw_responses)} reponses brutes -> {path}")
    print()
    return path


# Étape 2 : Transform - nettoyage, normalisation
def transform(path: str) -> pd.DataFrame:
    print("Transform : nettoyage des donnees...")

    with open(path, "r", encoding="utf-8") as f:
        raw_responses = json.load(f)

    rows = []
    for raw in raw_responses:
        row = openweather.transform(raw)
        if row:
            rows.append(row)

    df = pd.DataFrame(rows)

    if not df.empty:
        df = df.drop_duplicates(subset=["source", "city_code", "collected_at"])

    print(f"   {len(df)} lignes pretes.")
    print()
    return df


# Étape 3 : Load — insertion en base
def load(df: pd.DataFrame) -> int:
    print("Load : insertion en base PostgreSQL...")
    inserted = insert_weather(df)
    print()
    return inserted


# Étape 4 : Affichage du résumé
def print_summary(rows) -> None:
    if not rows:
        print("   (aucune donnée en base)")
        return

    print(f"   {'Source':<12} {'Ville':<20} {'Pays':<6} {'Temp':>8} {'Meteo':<22} {'Collecte le'}")
    for row in rows:
        source, city, country, temperature, weather_desc, collected_at = row

        temp_str = f"{temperature:.1f}°C" if temperature is not None else "N/A"
        desc_str = weather_desc if weather_desc else "N/A"
        date_str = collected_at.strftime("%Y-%m-%d %H:%M") if collected_at else "N/A"

        print(f"   {source:<12} {city:<20} {country:<6} {temp_str:>8} {desc_str:<22} {date_str}")


# Pipeline complet
def run_pipeline() -> None:
    print("PIPELINE METEO - ETL -> PostgreSQL")
    print()

    # Vérification BDD
    print("Vérification de la connexion PostgreSQL...")
    if not test_connection():
        print()
        print("Arrêt du pipeline : impossible de se connecter à la base.")
        print("Vérifie que Docker est lancé : docker compose ps")
        return
    print()

    # Extract
    raw_path = extract(DESTINATIONS)

    # Transform
    df = transform(raw_path)

    if df.empty:
        print("Aucune donnée après transformation. Arrêt du pipeline.")
        return

    # Aperçu
    print("   Aperçu :")
    preview_cols = ["source", "city", "country", "temperature", "weather_desc"]
    print(df[preview_cols].to_string(index=False))
    print()

    # Load
    load(df)

    # Vérification
    print("Résumé des dernières mesures par ville :")
    rows = query_latest_weather()
    print_summary(rows)
    print()

    print("Pipeline terminé avec succès.")


# Point d'entrée
if __name__ == "__main__":
    run_pipeline()