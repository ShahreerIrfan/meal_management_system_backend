"""
Vercel serverless function entry point.
Wraps the Django WSGI application for Vercel's Python runtime.
"""
import os
import subprocess

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Run collectstatic at cold start
subprocess.run(["python", "manage.py", "collectstatic", "--noinput"], check=False)

from django.core.wsgi import get_wsgi_application

app = application = get_wsgi_application()
