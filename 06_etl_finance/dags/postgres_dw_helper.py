"""
Utilitaires pour le data warehouse PostgreSQL.
"""

import os
import pandas as pd
import psycopg2


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DW_DB_HOST", "postgres-dw"),
        port=int(os.getenv("DW_DB_PORT", "5432")),
        database=os.getenv("DW_DB_NAME", "finance_dw"),
        user=os.getenv("DW_DB_USER", "dw_user"),
        password=os.getenv("DW_DB_PASSWORD", "dw_pass"),
    )


def truncate_tables(tables: list[str]) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            for table in tables:
                cur.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE")
        conn.commit()
    print(f"Tables vidées : {tables}")


def insert_dataframe(df: pd.DataFrame, table: str, columns: list[str]) -> int:
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
    sql = f"SELECT {business_col}, {key_col} FROM {table}"
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            return {row[0]: row[1] for row in cur.fetchall()}


def _to_native(value):
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value