# Parler à PostgreSQL

from sqlalchemy import create_engine, text
from config import DATABASE_URL

# Crée le "moteur" de connexion
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    future=True,
)

# Test de connexion
def test_connection() -> bool:
    try:
        with engine.connect() as conn:
            version = conn.execute(text("SELECT version();")).scalar()
            # On ne garde que la première partie avant la virgule
            print(f"Connecté à : {version.split(',')[0]}")
            return True

    except Exception as e:
        print(f"Impossible de se connecter à PostgreSQL : {e}")
        return False


def get_or_create_city(conn, row) -> int:
    """
    Récupère l'id d'une ville existante, ou la crée si absente.
    Identification par le couple (source, city_code).
    """
    result = conn.execute(
        text("""
            INSERT INTO cities (city_code, source, name, country, latitude, longitude)
            VALUES (:code, :source, :name, :country, :lat, :lon)
            ON CONFLICT (source, city_code) DO UPDATE
                SET name = EXCLUDED.name,
                    country = EXCLUDED.country,
                    latitude = EXCLUDED.latitude,
                    longitude = EXCLUDED.longitude
            RETURNING id;
        """),
        {
            "code": int(row["city_code"]),
            "source": row["source"],
            "name": row["city"],
            "country": row["country"],
            "lat": _safe_float(row["latitude"]),
            "lon": _safe_float(row["longitude"]),
        }
    ).fetchone()
    return result[0]


def insert_weather(df):
    if df.empty:
        print("Aucune donnée à insérer.")
        return 0

    inserted = 0

    with engine.begin() as conn:
        for _, row in df.iterrows():
            city_id = get_or_create_city(conn, row)

            result = conn.execute(
                text("""
                    INSERT INTO weather_data (
                        city_id, temperature, feels_like, temp_min, temp_max,
                        humidity, pressure, weather_main, weather_desc,
                        wind_speed, wind_deg, clouds, collected_at
                    )
                    VALUES (
                        :city_id, :temp, :feels, :temp_min, :temp_max,
                        :hum, :press, :wmain, :wdesc,
                        :wind, :wind_deg, :clouds, :collected
                    )
                    ON CONFLICT (city_id, collected_at) DO NOTHING
                    RETURNING id;
                """),
                {
                    "city_id": city_id,
                    "temp": _safe_float(row["temperature"]),
                    "feels": _safe_float(row["feels_like"]),
                    "temp_min": _safe_float(row.get("temp_min")),
                    "temp_max": _safe_float(row.get("temp_max")),
                    "hum": _safe_int(row["humidity"]),
                    "press": _safe_int(row["pressure"]),
                    "wmain": row["weather_main"],
                    "wdesc": row["weather_desc"],
                    "wind": _safe_float(row.get("wind_speed")),
                    "wind_deg": _safe_int(row.get("wind_deg")),
                    "clouds": _safe_int(row.get("clouds")),
                    "collected": row["collected_at"],
                }
            ).fetchone()

            if result:
                inserted += 1

    print(f"{inserted}/{len(df)} enregistrements insérés.")
    return inserted

# Convertit une valeur en float, ou None si invalide.
def _safe_float(value):
    if value is None:
        return None
    try:
        f = float(value)
        if f != f: # NaN != NaN est toujours vrai
            return None
        return f
    except (TypeError, ValueError):
        return None

# Convertit une valeur en int, ou None si invalide.
def _safe_int(value):
    if value is None:
        return None
    try:
        f = float(value)
        if f != f:  
            return None
        return int(f)
    except (TypeError, ValueError):
        return None

# Récupère la mesure la plus récente pour chaque ville
def query_latest_weather():
    query = text("""
        SELECT DISTINCT ON (c.id)
            c.source,
            c.name,
            c.country,
            w.temperature,
            w.weather_desc,
            w.collected_at
        FROM weather_data w
        JOIN cities c ON c.id = w.city_id
        ORDER BY c.id, w.collected_at DESC;
    """)

    with engine.connect() as conn:
        return conn.execute(query).fetchall()

# Récupère les N dernières mesures, toutes villes confondues( Utile pour du debug rapide)
def query_all_weather(limit: int = 20):
    query = text("""
        SELECT
            c.name, c.country,
            w.temperature, w.humidity, w.pressure,
            w.weather_main, w.weather_desc,
            w.wind_speed, w.clouds,
            w.collected_at
        FROM weather_data w
        JOIN cities c ON c.id = w.city_id
        ORDER BY w.collected_at DESC
        LIMIT :limit;
    """)

    with engine.connect() as conn:
        return conn.execute(query, {"limit": limit}).fetchall()


# Test rapide (exécution directe)
if __name__ == "__main__":
    print("Test de connexion...")
    test_connection()

    print("\nDernières mesures par ville :")
    for row in query_latest_weather():
        source, city, country, temperature, weather_desc, collected_at = row
        print(f"  [{source}] {city} ({country}) : {temperature}°C - {weather_desc} ({collected_at})")