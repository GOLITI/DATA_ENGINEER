#!/bin/bash
set -e

echo "=== Airflow initialization ==="

echo "Waiting for PostgreSQL..."
until airflow db check; do
    echo "  PostgreSQL not ready, retrying in 2s..."
    sleep 2
done
echo "  PostgreSQL is ready."

echo "Migrating Airflow metadata database..."
airflow db migrate

echo "Creating admin user (if not exists)..."
airflow users create \
    --username "${AIRFLOW_ADMIN_USER}" \
    --password "${AIRFLOW_ADMIN_PASSWORD}" \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email "${AIRFLOW_ADMIN_EMAIL}" \
    || echo "  Admin user already exists, skipping."

echo "Starting scheduler..."
airflow scheduler &

echo "Starting webserver..."
exec airflow webserver