# Point d'entrée du pipeline météo.

from config import DESTINATIONS
from sources import openweather
from database import (
    test_connection,
    insert_weather,
    query_latest_weather,
)
import pandas as pd


# Registre des sources actives.
# Pour ajouter une source : créer sources/xxx.py puis l'ajouter ici.
ACTIVE_SOURCES = [
    openweather,
    # meteofrance,     # décommenter le jour où on l'active
]


# Étape 1 : Collecte et transformation via toutes les sources actives.
def collect_and_transform(destinations: list[dict]) -> pd.DataFrame:
    print(f"Collecte via {len(ACTIVE_SOURCES)} source(s) pour {len(destinations)} villes...")

    all_rows = []

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

            row = source_module.transform(raw)
            if not row:
                print("ECHEC (transformation)")
                continue

            all_rows.append(row)
            print("OK")

    # Convertit en DataFrame
    df = pd.DataFrame(all_rows)

    if not df.empty:
        # Doublon si même (source, city_code, collected_at)
        df = df.drop_duplicates(subset=["source", "city_code", "collected_at"])

    print(f"   {len(df)} lignes prêtes à être insérées.")
    print()
    return df


# Étape 4 : Affichage du résumé.
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


# Pipeline complet.
def run_pipeline() -> None:
    print("PIPELINE METEO - multi-source -> PostgreSQL")
    print()

    # Étape 1 : Vérifier la connexion BDD
    print("Vérification de la connexion PostgreSQL...")
    if not test_connection():
        print()
        print("Arrêt du pipeline : impossible de se connecter à la base.")
        print("Vérifie que Docker est lancé : docker compose ps")
        return
    print()

    # Étape 2 et 3 : Collecte et transformation
    df = collect_and_transform(DESTINATIONS)

    if df.empty:
        print("Aucune donnée collectée. Arrêt du pipeline.")
        return

    # Aperçu
    print("   Aperçu :")
    preview_cols = ["source", "city", "country", "temperature", "weather_desc"]
    print(df[preview_cols].to_string(index=False))
    print()

    # Étape 4 : Insertion
    print("Insertion en base PostgreSQL...")
    insert_weather(df)
    print()

    # Étape 5 : Vérification
    print("Résumé des dernières mesures par ville :")
    rows = query_latest_weather()
    print_summary(rows)
    print()

    print("Pipeline terminé avec succès.")


# Point d'entrée
if __name__ == "__main__":
    run_pipeline()