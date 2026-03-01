#!/bin/bash
set -e

echo "=== Installing dependencies ==="
pip install -r requirements.txt

echo "=== Collecting static files ==="
python manage.py collectstatic --noinput

echo "=== Running database migrations ==="
python manage.py migrate --noinput

echo "=== Seeding permissions ==="
python -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from apps.permissions.services import seed_permissions
seed_permissions()
print('Permissions seeded successfully')
"

echo "=== Verifying database connection ==="
python -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute('SELECT 1')
print('Database connection OK:', connection.vendor)
"

echo "=== Build complete ==="
