#!/bin/sh
set -e

echo "==> Applying database migrations..."
python manage.py migrate --noinput

if [ "${SEED_DEMO_DATA:-1}" = "1" ]; then
    echo "==> Seeding demo catalog..."
    python manage.py seed
fi

echo "==> Collecting static files..."
python manage.py collectstatic --noinput

echo "==> Starting gunicorn on 0.0.0.0:${PORT:-8000}"
exec gunicorn config.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers "${WEB_CONCURRENCY:-3}" \
    --timeout 60 \
    --access-logfile - \
    --error-logfile -
