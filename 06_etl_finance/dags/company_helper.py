"""
Lecture du référentiel entreprises depuis company-db.
"""

import os
import pandas as pd
import psycopg2


def get_company_connection():
    return psycopg2.connect(
        host=os.getenv("COMPANY_DB_HOST", "company-db"),
        port=int(os.getenv("COMPANY_DB_PORT", "5432")),
        database=os.getenv("COMPANY_DB_NAME", "company"),
        user=os.getenv("COMPANY_DB_USER", "company_user"),
        password=os.getenv("COMPANY_DB_PASSWORD", "company_pass"),
    )


def fetch_companies() -> pd.DataFrame:
    sql = "SELECT ticker, name, sector, region, country FROM companies ORDER BY ticker"
    with get_company_connection() as conn:
        return pd.read_sql(sql, conn)