# DAG Airflow : pipeline météo
# 3 tâches distinctes : extract, transform, load

import sys
import json
import pandas as pd
from datetime import datetime, timedelta

from airflow.decorators import dag, task

sys.path.insert(0, "/opt/airflow")

from sources import openweather
from database import test_connection, insert_weather
from config import DESTINATIONS


default_args = {
    "owner": "data_team",
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}


@dag(
    dag_id="weather_etl",
    description="Collecte météo OpenWeather -> PostgreSQL",
    schedule="0 * * * *",
    start_date=datetime(2026, 9, 1),
    catchup=False,
    default_args=default_args,
    tags=["weather", "etl", "openweather"],
)
def weather_etl():

    # Task 1 : Extract - appel API, écriture JSON brut
    @task
    def extract() -> str:
        """
        Appelle l'API OpenWeather pour chaque destination.
        Écrit les réponses brutes dans un fichier JSON.
        Retourne le chemin du fichier.
        """
        raw_responses = []

        for dest in DESTINATIONS:
            raw = openweather.fetch(dest["city"], dest["country"])
            if raw:
                raw_responses.append(raw)

        path = "/tmp/weather_raw.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(raw_responses, f, ensure_ascii=False)

        print(f"Extract : {len(raw_responses)} reponses brutes -> {path}")
        return path

    # Task 2 : Transform — nettoyage, normalisation
    @task
    def transform(path: str) -> str:
        """
        Lit le JSON brut, normalise chaque reponse,
        écrit un DataFrame propre au format Parquet.
        Retourne le chemin du fichier Parquet.
        """
        with open(path, "r", encoding="utf-8") as f:
            raw_responses = json.load(f)

        rows = []
        for raw in raw_responses:
            row = openweather.transform(raw)
            if row:
                rows.append(row)

        df = pd.DataFrame(rows)

        if not df.empty:
            df = df.drop_duplicates(
                subset=["source", "city_code", "collected_at"]
            )

        path_out = "/tmp/weather_clean.parquet"
        df.to_parquet(path_out, index=False)

        print(f"Transform : {len(df)} lignes -> {path_out}")
        return path_out

    # Task 3 : Load - insertion en base
    @task
    def load(path: str) -> int:
        """
        Lit le Parquet, vérifie la connexion BDD,
        puis insère les données en base.
        Retourne le nombre de lignes insérées.
        """
        if not test_connection():
            raise RuntimeError("Connexion PostgreSQL impossible")

        df = pd.read_parquet(path)

        if df.empty:
            print("Aucune donnée à insérer")
            return 0

        inserted = insert_weather(df)
        return inserted

    # Dépendances entre tâches
    raw_path = extract()
    clean_path = transform(raw_path)
    load(clean_path)


weather_etl()