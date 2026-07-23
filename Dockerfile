FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend/ ./backend/
COPY rom_couture_final/ ./rom_couture_final/

ENV DJANGO_SECRET_KEY="change-this-in-production" \
    DJANGO_DEBUG="False" \
    DJANGO_ALLOWED_HOSTS="tspcouture.com,www.tspcouture.com,admin.tspcouture.com" \
    EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend"

RUN cd backend && python manage.py collectstatic --noinput

RUN bash -c 'cat > /etc/nginx/conf.d/default.conf <<EOF
server {
    listen 8000;
    server_name tspcouture.com www.tspcouture.com admin.tspcouture.com;

    client_max_body_size 50M;

    location /static/ {
        alias /app/backend/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /app/backend/media/;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /cms-admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location = / {
        if (\$host = admin.tspcouture.com) {
            return 301 /cms-admin/;
        }
        root /app/rom_couture_final;
        index index.html;
    }

    location / {
        root /app/rom_couture_final;
        index index.html;
        try_files \$uri \$uri/ \$uri.html =404;
    }
}
EOF'

RUN bash -c 'cat > /docker-entrypoint.sh <<EOF
#!/bin/bash
set -e

cd /app/backend

if [ "\$DB_ENGINE" = "django.db.backends.postgresql" ]; then
    echo "Waiting for PostgreSQL..."
    while ! python -c "import psycopg2; psycopg2.connect(host=\$DB_HOST, user=\$DB_USER, password=\$DB_PASSWORD, dbname=\$DB_NAME)" 2>/dev/null; do
        sleep 1
    done
    echo "PostgreSQL is ready"
fi

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Starting services..."
nginx
exec gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 2 --access-logfile - --error-logfile -
EOF'

RUN chmod +x /docker-entrypoint.sh

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/health/ || exit 1

ENTRYPOINT ["/docker-entrypoint.sh"]
