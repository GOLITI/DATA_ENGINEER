-- SCHÉMA EN ÉTOILE - SALES DATA WAREHOUSE (REDSHIFT)---


-- Dimension DATE
CREATE TABLE IF NOT EXISTS dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    day INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name VARCHAR(20) NOT NULL,
    is_weekend OOLEAN NOT NULL
);

-- Dimension CUSTOMER
CREATE TABLE IF NOT EXISTS dim_customer (
    customer_key SERIAL PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL UNIQUE,
    customer_name VARCHAR(100) NOT NULL,
    segment VARCHAR(50) NOT NULL
);

-- Dimension PRODUCT
CREATE TABLE IF NOT EXISTS dim_product (
    product_key SERIAL PRIMARY KEY,
    product_id VARCHAR(30) NOT NULL UNIQUE,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL,
    sub_category VARCHAR(50) NOT NULL
);

-- Dimension LOCATION
CREATE TABLE IF NOT EXISTS dim_location (
    location_key SERIAL PRIMARY KEY,
    country VARCHAR(50) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    postal_code INTEGER,
    region VARCHAR(20) NOT NULL,
    UNIQUE(country, city, state, postal_code)
);

-- Dimension SHIP MODE
CREATE TABLE IF NOT EXISTS dim_ship_mode (
    ship_mode_key SERIAL PRIMARY KEY,
    ship_mode_name VARCHAR(50) NOT NULL UNIQUE
);

-- Dimension COUNTRY (NOUVEAU - enrichie par l'API)
CREATE TABLE IF NOT EXISTS dim_country (
    country_key SERIAL PRIMARY KEY,
    country_code VARCHAR(2) NOT NULL UNIQUE,
    country_name VARCHAR(100) NOT NULL,
    region VARCHAR(50),
    subregion VARCHAR(50),
    population BIGINT,
    area NUMERIC(15, 2)
);


-- Table de FAITS principale : VENTES
CREATE TABLE IF NOT EXISTS fact_sales (
    sale_key SERIAL PRIMARY KEY,
    order_id VARCHAR(30) NOT NULL,
    row_id INTEGER NOT NULL,
    date_key INTEGER NOT NULL,
    customer_key INTEGER NOT NULL,
    product_key INTEGER NOT NULL,
    location_key INTEGER NOT NULL,
    ship_mode_key INTEGER NOT NULL,
    sales NUMERIC(12, 2) NOT NULL,
    quantity INTEGER NOT NULL,
    discount NUMERIC(5, 2) NOT NULL,
    profit NUMERIC(12, 2) NOT NULL,
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
    FOREIGN KEY (product_key) REFERENCES dim_product(product_key),
    FOREIGN KEY (location_key) REFERENCES dim_location(location_key),
    FOREIGN KEY (ship_mode_key) REFERENCES dim_ship_mode(ship_mode_key),
    UNIQUE(order_id, row_id)
);

-- Table de FAITS secondaire : OBJECTIFS
CREATE TABLE IF NOT EXISTS fact_sales_targets (
    target_key SERIAL PRIMARY KEY,
    region VARCHAR(20) NOT NULL,
    year INTEGER NOT NULL,
    target NUMERIC(12, 2) NOT NULL,
    UNIQUE(region, year)
);

-- INDEX
CREATE INDEX IF NOT EXISTS idx_fact_date     ON fact_sales(date_key);
CREATE INDEX IF NOT EXISTS idx_fact_customer ON fact_sales(customer_key);
CREATE INDEX IF NOT EXISTS idx_fact_product  ON fact_sales(product_key);