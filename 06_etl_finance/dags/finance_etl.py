"""
Pipeline ETL financier multi-sources :
  - API yfinance (prix boursiers)
  - Fichier Excel (objectifs internes)
  - PostgreSQL company (référentiel entreprises)
Destination : PostgreSQL Data Warehouse (schéma en étoile)
"""

import sys
import pandas as pd
from datetime import datetime, timedelta

from airflow.decorators import dag, task

sys.path.insert(0, "/opt/airflow/dags")
from postgres_dw_helper import (
    truncate_tables, insert_dataframe, get_key_mapping,
)
from company_helper import fetch_companies


TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA",
           "NVDA", "JPM", "V", "JNJ", "WMT"]


@dag(
    dag_id="finance_etl",
    description="ETL financier multi-sources -> PostgreSQL DW",
    schedule="@hourly",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    default_args={
        "owner": "data_team",
        "retries": 2,
        "retry_delay": timedelta(minutes=2),
    },
    tags=["finance", "etl", "postgres"],
)
def finance_etl():

   
    # SOURCE 1 — yfinance
    @task
    def extract_prices() -> str:
        import yfinance as yf
        print(f"Téléchargement des prix pour {len(TICKERS)} tickers...")
        all_data = []

        for ticker in TICKERS:
            df = yf.download(ticker, period="2y", progress=False)
            if df.empty:
                print(f"  {ticker} : aucune donnée")
                continue

            # Aplatir un éventuel MultiIndex sur les colonnes
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            df = df.reset_index()

            # Normaliser le nom des colonnes (lowercase, sans espaces)
            df.columns = [str(c).lower().replace(" ", "_") for c in df.columns]

            # S'assurer que la colonne date existe
            if "date" not in df.columns and "datetime" in df.columns:
                df = df.rename(columns={"datetime": "date"})

            df["ticker"] = ticker
            all_data.append(df)
            print(f"  {ticker} : {len(df)} lignes, colonnes = {list(df.columns)}")

        if not all_data:
            raise ValueError("Aucune donnée récupérée")

        result = pd.concat(all_data, ignore_index=True)
        path = "/tmp/prices.parquet"
        result.to_parquet(path, index=False)
        print(f"  Total : {len(result)} lignes -> {path}")
        return path

    # SOURCE 2 — Excel
    @task
    def extract_excel() -> str:
        print("Lecture du fichier Excel interne...")
        df = pd.read_excel("/opt/airflow/data/financial_targets.xlsx")
        path = "/tmp/targets.parquet"
        df.to_parquet(path, index=False)
        print(f"  {len(df)} objectifs -> {path}")
        return path

    # SOURCE 3 — PostgreSQL company
    @task
    def extract_company() -> str:
        print("Lecture du référentiel entreprises...")
        df = fetch_companies()
        path = "/tmp/company.parquet"
        df.to_parquet(path, index=False)
        print(f"  {len(df)} entreprises -> {path}")
        return path

    # LOAD — dimensions
    @task
    def load_dimensions(company_path: str,
                        targets_path: str,
                        prices_path: str) -> str:
        company = pd.read_parquet(company_path)
        targets = pd.read_parquet(targets_path)
        prices = pd.read_parquet(prices_path)

        truncate_tables(["fact_stock_prices", "dim_date", "dim_ticker"])

        # --- dim_ticker ---
        dim_ticker = company.merge(targets, on="ticker", how="left")
        dim_ticker = dim_ticker.rename(columns={"name": "company_name"})
        dim_ticker = dim_ticker[
            ["ticker", "company_name", "sector", "region", "country",
             "target_revenue", "target_margin", "fiscal_year"]
        ]
        dim_ticker.insert(0, "ticker_key", range(1, len(dim_ticker) + 1))
        insert_dataframe(dim_ticker, "dim_ticker", list(dim_ticker.columns))

        # --- dim_date ---
        prices["date"] = pd.to_datetime(prices["date"])
        all_dates = prices["date"].drop_duplicates().sort_values()
        dim_date = pd.DataFrame({"full_date": all_dates})
        dim_date["date_key"] = dim_date["full_date"].dt.strftime("%Y%m%d").astype(int)
        dim_date["year"] = dim_date["full_date"].dt.year
        dim_date["quarter"] = dim_date["full_date"].dt.quarter
        dim_date["month"] = dim_date["full_date"].dt.month
        dim_date["month_name"] = dim_date["full_date"].dt.strftime("%B")
        dim_date["day"] = dim_date["full_date"].dt.day
        dim_date["day_of_week"] = dim_date["full_date"].dt.dayofweek
        dim_date["day_name"] = dim_date["full_date"].dt.strftime("%A")
        dim_date["is_weekend"] = dim_date["day_of_week"] >= 5
        dim_date = dim_date[
            ["date_key", "full_date", "year", "quarter", "month",
             "month_name", "day", "day_of_week", "day_name", "is_weekend"]
        ]
        insert_dataframe(dim_date, "dim_date", list(dim_date.columns))

        return prices_path

    # LOAD — faits
    @task
    def load_fact(prices_path: str) -> int:
        prices = pd.read_parquet(prices_path)
        prices["date"] = pd.to_datetime(prices["date"])
        prices = prices.sort_values(["ticker", "date"])

        # Indicateurs techniques
        prices["daily_return"] = prices.groupby("ticker")["close"].pct_change()
        prices["sma_20"] = prices.groupby("ticker")["close"].transform(
            lambda x: x.rolling(20).mean()
        )
        prices["sma_50"] = prices.groupby("ticker")["close"].transform(
            lambda x: x.rolling(50).mean()
        )
        prices["volatility_30d"] = prices.groupby("ticker")["daily_return"].transform(
            lambda x: x.rolling(30).std()
        )

        ticker_map = get_key_mapping("dim_ticker", "ticker", "ticker_key")

        fact = pd.DataFrame()
        fact["date_key"] = prices["date"].dt.strftime("%Y%m%d").astype(int)
        fact["ticker_key"] = prices["ticker"].map(ticker_map)
        fact["open_price"] = prices["open"]
        fact["high_price"] = prices["high"]
        fact["low_price"] = prices["low"]
        fact["close_price"] = prices["close"]
        fact["volume"] = prices["volume"]
        fact["daily_return"] = prices["daily_return"]
        fact["sma_20"] = prices["sma_20"]
        fact["sma_50"] = prices["sma_50"]
        fact["volatility_30d"] = prices["volatility_30d"]

        fact = fact.dropna(subset=["ticker_key"])
        fact["ticker_key"] = fact["ticker_key"].astype(int)

        return insert_dataframe(fact, "fact_stock_prices", list(fact.columns))

    # DÉPENDANCES
    prices_path = extract_prices()
    targets_path = extract_excel()
    company_path = extract_company()

    prices_path = load_dimensions(company_path, targets_path, prices_path)
    load_fact(prices_path)


finance_etl()