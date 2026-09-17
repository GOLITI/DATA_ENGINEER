"""
Lecture des objectifs de vente depuis PostgreSQL source.
"""

import os
import pandas as pd
import psycopg2


def get_targets_connection():
    return psycopg2.connect(
        host=os.getenv("TARGETS_DB_HOST", "sales-targets-db"),
        port=int(os.getenv("TARGETS_DB_PORT", "5432")),
        database=os.getenv("TARGETS_DB_NAME", "sales_targets"),
        user=os.getenv("TARGETS_DB_USER", "targets_user"),
        password=os.getenv("TARGETS_DB_PASSWORD", "targets_pass"),
    )


def fetch_targets() -> pd.DataFrame:
    sql = "SELECT region, year, target FROM sales_targets ORDER BY region, year"
    with get_targets_connection() as conn:
        return pd.read_sql(sql, conn)