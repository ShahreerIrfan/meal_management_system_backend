"""
"""
Vercel serverless function entry point.
Wraps the Django WSGI application for Vercel's Python runtime.

On cold start: runs migrations + seeds permissions via Django Python API.
"""
import os
import logging

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

logger = logging.getLogger(__name__)

# ── Cold-start: run migrations via Django API (no subprocess) ──
try:
    from django.core.management import call_command
    call_command("migrate", "--noinput", verbosity=0)
except Exception as e:
    logger.warning(f"Auto-migrate skipped: {e}")

# ── Cold-start: seed permissions ──
try:
    from apps.permissions.services import seed_permissions
    seed_permissions()
except Exception as e:
    logger.warning(f"Permission seeding skipped: {e}")

from django.core.wsgi import get_wsgi_application

app = application = get_wsgi_application()
