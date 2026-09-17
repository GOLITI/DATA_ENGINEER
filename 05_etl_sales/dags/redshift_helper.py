"""
Fonctions utilitaires pour interagir avec Redshift local.
"""

import os
import pandas as pd
import psycopg2


def get_connection():
    """Ouvre une connexion directe au PostgreSQL de Redshift local."""
    return psycopg2.connect(
        host=os.getenv("REDSHIFT_HOST", "redshift"),
        port=int(os.getenv("REDSHIFT_PORT", "5433")),
        database=os.getenv("REDSHIFT_DB", "sales_db"),
        user=os.getenv("REDSHIFT_USER", "admin"),
        password=os.getenv("REDSHIFT_PASSWORD", "admin123"),
    )


def truncate_all_tables():
    """Vide toutes les tables pour repartir proprement."""
    tables = [
        "fact_sales",
        "fact_sales_targets",
        "dim_country",
        "dim_customer",
        "dim_date",
        "dim_location",
        "dim_product",
        "dim_ship_mode",
    ]
    with get_connection() as conn:
        with conn.cursor() as cur:
            for table in tables:
                cur.execute(f"TRUNCATE TABLE {table} CASCADE")
        conn.commit()
    print(f"Tables vidées : {tables}")


def insert_dataframe(df: pd.DataFrame, table: str, columns: list[str]) -> int:
    """Insère un DataFrame dans une table."""
    if df.empty:
        return 0

    cols = ", ".join(columns)
    placeholders = ", ".join(["%s"] * len(columns))
    sql = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"

    rows = []
    for _, row in df.iterrows():
        rows.append([_to_native(row[c]) for c in columns])

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.executemany(sql, rows)
        conn.commit()

    print(f"  {table} : {len(rows)} lignes insérées")
    return len(rows)


def get_key_mapping(table: str, business_col: str, key_col: str) -> dict:
    """Retourne {valeur_metier: cle_surrogate} pour une dimension."""
    sql = f"SELECT {business_col}, {key_col} FROM {table}"
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            return {row[0]: row[1] for row in cur.fetchall()}


def get_location_mapping() -> dict:
    """Retourne {(country, city, state, postal_code): location_key}."""
    sql = "SELECT country, city, state, postal_code, location_key FROM dim_location"
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            return {
                (row[0], row[1], row[2], row[3]): row[4]
                for row in cur.fetchall()
            }


def _to_native(value):
    """Convertit les types numpy/pandas en types Python natifs."""
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value