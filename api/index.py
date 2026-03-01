"""
Vercel serverless function entry point.
Wraps the Django WSGI application for Vercel's Python runtime.
"""
import os
import subprocess
import logging

logger = logging.getLogger(__name__)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# ── Cold-start tasks ────────────────────────────────────────
try:
    subprocess.run(
        ["python", "manage.py", "collectstatic", "--noinput"],
        check=False,
        capture_output=True,
    )
except Exception:
    pass

# Auto-run migrations on cold start (safe for PostgreSQL)
try:
    subprocess.run(
        ["python", "manage.py", "migrate", "--noinput"],
        check=False,
        capture_output=True,
    )
except Exception:
    pass

# Seed permissions after migrations
try:
    import django
    django.setup()
    from apps.permissions.services import seed_permissions
    seed_permissions()
except Exception as e:
    logger.warning(f"Permission seeding skipped: {e}")

from django.core.wsgi import get_wsgi_application

app = application = get_wsgi_application()
