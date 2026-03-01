# Vercel serverless function entry point.
# Wraps the Django WSGI application for Vercel Python runtime.
# On cold start: runs migrations and seeds permissions.
import os
import logging

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Debug: log whether DATABASE_URL is set on Vercel
_db_url = os.environ.get("DATABASE_URL", "")
if _db_url:
    print(f"[Vercel] DATABASE_URL is SET ({_db_url[:40]}...)")
else:
    print("[Vercel] WARNING: DATABASE_URL is NOT SET — will fall back to SQLite!")

import django
django.setup()

logger = logging.getLogger(__name__)

# Cold-start: run migrations via Django API
try:
    from django.core.management import call_command
    call_command("migrate", "--noinput", verbosity=0)
    logger.info("Migrations applied successfully")
except Exception as e:
    logger.warning("Auto-migrate skipped: %s", e)

# Cold-start: seed permissions
try:
    from apps.permissions.services import seed_permissions
    seed_permissions()
except Exception as e:
    logger.warning("Permission seeding skipped: %s", e)

from django.core.wsgi import get_wsgi_application

app = application = get_wsgi_application()
