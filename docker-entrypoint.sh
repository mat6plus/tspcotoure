#!/bin/bash
set -e

cd /app/backend

if [ "$DB_ENGINE" = "django.db.backends.postgresql" ]; then
    echo "Waiting for PostgreSQL..."
    while ! python -c "import psycopg2; psycopg2.connect(host=$DB_HOST, user=$DB_USER, password=$DB_PASSWORD, dbname=$DB_NAME)" 2>/dev/null; do
        sleep 1
    done
    echo "PostgreSQL is ready"
fi

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Starting services..."
nginx
exec gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 2 --access-logfile - --error-logfile -
