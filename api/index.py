# Vercel serverless function entry point.
# Optimized for fast cold starts.
import os
import logging

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from django.core.wsgi import get_wsgi_application
app = application = get_wsgi_application()

# Cold-start: run migrations only if needed (check flag to avoid re-running)
logger = logging.getLogger(__name__)
_migrated = False

def _cold_start_tasks():
    global _migrated
    if _migrated:
        return
    try:
        from django.core.management import call_command
        call_command("migrate", "--noinput", verbosity=0)
    except Exception as e:
        logger.warning("Auto-migrate skipped: %s", e)
    try:
        from apps.permissions.services import seed_permissions
        seed_permissions()
    except Exception as e:
        logger.warning("Permission seeding skipped: %s", e)
    _migrated = True

# Run once on import
_cold_start_tasks()
