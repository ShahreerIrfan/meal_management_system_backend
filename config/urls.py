"""
Root URL configuration.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.db import connection
import os


def health_check(request):
    """Diagnostic endpoint to verify DB and env."""
    db_ok = False
    db_engine = ""
    db_error = ""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_ok = True
        db_engine = connection.vendor
    except Exception as e:
        db_error = str(e)

    return JsonResponse({
        "status": "ok" if db_ok else "error",
        "database": {
            "connected": db_ok,
            "engine": db_engine,
            "error": db_error,
        },
        "environment": {
            "VERCEL": os.environ.get("VERCEL", "not set"),
            "DATABASE_URL_set": bool(os.environ.get("DATABASE_URL")),
            "DEBUG": os.environ.get("DEBUG", "not set"),
        },
    })


def root_view(request):
    return JsonResponse({"message": "Meal Management API", "health": "/health/"})


urlpatterns = [
    path("", root_view),
    path("health/", health_check),
    path("admin/", admin.site.urls),
    path("api/v1/auth/", include("apps.accounts.urls")),
    path("api/v1/flats/", include("apps.flats.urls")),
    path("api/v1/permissions/", include("apps.permissions.urls")),
    path("api/v1/meals/", include("apps.meals.urls")),
    path("api/v1/expenses/", include("apps.expenses.urls")),
    path("api/v1/analytics/", include("apps.analytics.urls")),
    path("api/v1/core/", include("apps.core.urls")),
]
