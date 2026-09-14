CREATE TABLE IF NOT EXISTS cities (
    id SERIAL PRIMARY KEY,
    city_code INTEGER NOT NULL,
    source VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(2) NOT NULL,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source, city_code),
    UNIQUE(name, country)
);

CREATE TABLE IF NOT EXISTS weather_data (
    id SERIAL PRIMARY KEY,
    city_id INTEGER NOT NULL REFERENCES cities(id) ON DELETE CASCADE,
    temperature DOUBLE PRECISION,
    feels_like DOUBLE PRECISION,
    temp_min DOUBLE PRECISION,
    temp_max DOUBLE PRECISION,
    humidity INTEGER CHECK (humidity BETWEEN 0 AND 100),
    pressure INTEGER,
    weather_main VARCHAR(50),
    weather_desc VARCHAR(255),
    wind_speed DOUBLE PRECISION,
    wind_deg INTEGER,
    clouds INTEGER CHECK (clouds BETWEEN 0 AND 100),
    collected_at TIMESTAMP NOT NULL,
    inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(city_id, collected_at)
);

CREATE INDEX IF NOT EXISTS idx_weather_city_date
    ON weather_data(city_id, collected_at DESC);