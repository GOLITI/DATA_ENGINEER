-- DESTINATION : schéma en étoile financier

CREATE TABLE IF NOT EXISTS dim_date (
    date_key        INTEGER PRIMARY KEY,
    full_date       DATE NOT NULL,
    year            INTEGER NOT NULL,
    quarter         INTEGER NOT NULL,
    month           INTEGER NOT NULL,
    month_name      VARCHAR(20) NOT NULL,
    day             INTEGER NOT NULL,
    day_of_week     INTEGER NOT NULL,
    day_name        VARCHAR(20) NOT NULL,
    is_weekend      BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_ticker (
    ticker_key      SERIAL PRIMARY KEY,
    ticker          VARCHAR(10) NOT NULL UNIQUE,
    company_name    VARCHAR(100) NOT NULL,
    sector          VARCHAR(50),
    region          VARCHAR(30),
    country         VARCHAR(50),
    target_revenue  NUMERIC(20, 2),
    target_margin   NUMERIC(10, 2),
    fiscal_year     INTEGER
);

CREATE TABLE IF NOT EXISTS fact_stock_prices (
    price_key       SERIAL PRIMARY KEY,
    date_key        INTEGER NOT NULL REFERENCES dim_date(date_key),
    ticker_key      INTEGER NOT NULL REFERENCES dim_ticker(ticker_key),
    open_price      NUMERIC(12, 4),
    high_price      NUMERIC(12, 4),
    low_price       NUMERIC(12, 4),
    close_price     NUMERIC(12, 4),
    volume          BIGINT,
    daily_return    NUMERIC(12, 8),
    sma_20          NUMERIC(12, 4),
    sma_50          NUMERIC(12, 4),
    volatility_30d  NUMERIC(12, 8)
);

CREATE INDEX IF NOT EXISTS idx_fact_date ON fact_stock_prices(date_key);
CREATE INDEX IF NOT EXISTS idx_fact_ticker ON fact_stock_prices(ticker_key);