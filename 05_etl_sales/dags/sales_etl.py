"""
Pipeline ETL multi-sources :
  - CSV Superstore (ventes)
  - API REST Countries (enrichissement pays)
  - PostgreSQL sales_targets (objectifs)
"""

import sys
import pandas as pd
from datetime import datetime, timedelta

from airflow.decorators import dag, task

sys.path.insert(0, "/opt/airflow/dags")
from redshift_helper import (
    truncate_all_tables, insert_dataframe,
    get_key_mapping, get_location_mapping,
)
from targets_helper import fetch_targets


DATA_FILE = "/opt/airflow/data/superstore.csv"


@dag(
    dag_id="sales_etl",
    description="ETL multi-sources -> Redshift (schéma en étoile)",
    schedule="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    default_args={
        "owner": "data_team",
        "retries": 2,
        "retry_delay": timedelta(minutes=2),
    },
    tags=["sales", "etl", "multi-source", "redshift"],
)
def sales_etl():

    # TASK 1 — EXTRACT CSV
    @task
    def extract_csv() -> str:
        print(f"Lecture de {DATA_FILE}...")
        df = pd.read_csv(DATA_FILE, encoding="latin-1")
        df["Order Date"] = pd.to_datetime(df["Order Date"], format="%m/%d/%Y")
        df["Ship Date"] = pd.to_datetime(df["Ship Date"], format="%m/%d/%Y")
        path = "/tmp/superstore.parquet"
        df.to_parquet(path, index=False)
        print(f"  {len(df)} lignes -> {path}")
        return path

    # TASK 2 — EXTRACT API (REST Countries)
    @task
    def extract_api() -> str:
        from api_client import fetch_all_countries, parse_countries
        print("Appel API REST Countries...")
        raw = fetch_all_countries()
        rows = parse_countries(raw)
        df = pd.DataFrame(rows)
        path = "/tmp/countries.parquet"
        df.to_parquet(path, index=False)
        print(f"  {len(df)} pays -> {path}")
        return path

    # TASK 3 — EXTRACT POSTGRES (sales_targets)
    @task
    def extract_targets() -> str:
        print("Lecture des objectifs de vente...")
        df = fetch_targets()
        path = "/tmp/targets.parquet"
        df.to_parquet(path, index=False)
        print(f"  {len(df)} objectifs -> {path}")
        return path

    # TASK 4 — LOAD DIMENSIONS
    @task
    def load_dimensions(csv_path: str, api_path: str) -> str:
        df = pd.read_parquet(csv_path)
        countries_df = pd.read_parquet(api_path)

        truncate_all_tables()

        # --- dim_country (depuis l'API) ---
        countries_df = countries_df.dropna(subset=["country_code"])
        countries_df = countries_df[
            countries_df["country_code"].astype(str).str.strip() != ""
        ]
        countries_df = countries_df.drop_duplicates(subset=["country_code"])
        insert_dataframe(countries_df, "dim_country", list(countries_df.columns))

        # --- dim_customer ---
        dim_customer = (
            df[["Customer ID", "Customer Name", "Segment"]]
            .drop_duplicates(subset=["Customer ID"])
            .rename(columns={"Customer ID": "customer_id",
                             "Customer Name": "customer_name",
                             "Segment": "segment"})
        )
        insert_dataframe(dim_customer, "dim_customer",
                         ["customer_id", "customer_name", "segment"])

        # --- dim_product ---
        dim_product = (
            df[["Product ID", "Product Name", "Category", "Sub-Category"]]
            .drop_duplicates(subset=["Product ID"])
            .rename(columns={"Product ID": "product_id",
                             "Product Name": "product_name",
                             "Category": "category",
                             "Sub-Category": "sub_category"})
        )
        insert_dataframe(dim_product, "dim_product",
                         ["product_id", "product_name", "category", "sub_category"])

        # --- dim_location ---
        dim_location = (
            df[["Country", "City", "State", "Postal Code", "Region"]]
            .drop_duplicates()
            .rename(columns={"Country": "country", "City": "city",
                             "State": "state", "Postal Code": "postal_code",
                             "Region": "region"})
        )
        insert_dataframe(dim_location, "dim_location",
                         ["country", "city", "state", "postal_code", "region"])

        # --- dim_ship_mode ---
        dim_ship_mode = (
            df[["Ship Mode"]].drop_duplicates()
            .rename(columns={"Ship Mode": "ship_mode_name"})
        )
        insert_dataframe(dim_ship_mode, "dim_ship_mode", ["ship_mode_name"])

        # --- dim_date ---
        all_dates = pd.concat([df["Order Date"], df["Ship Date"]]).drop_duplicates()
        dim_date = pd.DataFrame({"full_date": all_dates.sort_values()})
        dim_date["date_key"] = dim_date["full_date"].dt.strftime("%Y%m%d").astype(int)
        dim_date["year"] = dim_date["full_date"].dt.year
        dim_date["quarter"] = dim_date["full_date"].dt.quarter
        dim_date["month"] = dim_date["full_date"].dt.month
        dim_date["month_name"] = dim_date["full_date"].dt.strftime("%B")
        dim_date["day"] = dim_date["full_date"].dt.day
        dim_date["day_of_week"] = dim_date["full_date"].dt.dayofweek
        dim_date["day_name"] = dim_date["full_date"].dt.strftime("%A")
        dim_date["is_weekend"] = dim_date["day_of_week"] >= 5
        dim_date = dim_date[["date_key", "full_date", "year", "quarter", "month",
                             "month_name", "day", "day_of_week", "day_name", "is_weekend"]]
        insert_dataframe(dim_date, "dim_date", list(dim_date.columns))

        return csv_path

    # TASK 5 — LOAD FACTS
    @task
    def load_fact(csv_path: str, targets_path: str) -> int:
        df = pd.read_parquet(csv_path)
        targets_df = pd.read_parquet(targets_path)

        customer_map = get_key_mapping("dim_customer", "customer_id", "customer_key")
        product_map = get_key_mapping("dim_product", "product_id", "product_key")
        ship_mode_map = get_key_mapping("dim_ship_mode", "ship_mode_name", "ship_mode_key")
        location_map = get_location_mapping()

        fact = pd.DataFrame()
        fact["order_id"] = df["Order ID"]
        fact["row_id"] = df["Row ID"]
        fact["date_key"] = df["Order Date"].dt.strftime("%Y%m%d").astype(int)
        fact["customer_key"] = df["Customer ID"].map(customer_map)
        fact["product_key"] = df["Product ID"].map(product_map)
        fact["ship_mode_key"] = df["Ship Mode"].map(ship_mode_map)
        fact["location_key"] = df.apply(
            lambda r: location_map.get((r["Country"], r["City"], r["State"], r["Postal Code"])),
            axis=1,
        )
        fact["sales"] = df["Sales"]
        fact["quantity"] = df["Quantity"]
        fact["discount"] = df["Discount"]
        fact["profit"] = df["Profit"]

        n = insert_dataframe(fact, "fact_sales", list(fact.columns))

        # Table de faits secondaire : objectifs
        insert_dataframe(targets_df, "fact_sales_targets",
                         ["region", "year", "target"])

        return n

    # DÉPENDANCES
    csv_path = extract_csv()
    api_path = extract_api()
    targets_path = extract_targets()

    csv_path = load_dimensions(csv_path, api_path)
    load_fact(csv_path, targets_path)


sales_etl()