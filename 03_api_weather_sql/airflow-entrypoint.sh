#!/bin/bash
set -e

echo "=== Airflow initialization ==="

# 1. Attendre que PostgreSQL soit prêt
echo "Waiting for PostgreSQL at $DB_HOST:$DB_PORT..."
until airflow db check; do
    echo "  PostgreSQL not ready, retrying in 2s..."
    sleep 2
done
echo "  PostgreSQL is ready."

# 2. Migrer la DB (idempotent)
echo "Migrating Airflow metadata database..."
airflow db migrate

# 3. Créer l'utilisateur admin s'il n'existe pas
echo "Creating admin user (if not exists)..."
airflow users create \
    --username "${AIRFLOW_ADMIN_USER}" \
    --password "${AIRFLOW_ADMIN_PASSWORD}" \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email "${AIRFLOW_ADMIN_EMAIL}" \
    || echo "  Admin user already exists, skipping."

# 4. Lancer le scheduler en arrière-plan
echo "Starting scheduler..."
airflow scheduler &

# 5. Lancer le webserver au premier plan
echo "Starting webserver..."
exec airflow webserver