"""
Vercel serverless function entry point.
Wraps the Django WSGI application for Vercel's Python runtime.
"""
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from django.core.wsgi import get_wsgi_application

app = application = get_wsgi_application()
