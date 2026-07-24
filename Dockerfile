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

COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/health/ || exit 1

ENTRYPOINT ["/docker-entrypoint.sh"]
