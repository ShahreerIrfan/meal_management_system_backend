"""
Root URL configuration.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/", include("apps.accounts.urls")),
    path("api/v1/flats/", include("apps.flats.urls")),
    path("api/v1/permissions/", include("apps.permissions.urls")),
    path("api/v1/meals/", include("apps.meals.urls")),
    path("api/v1/expenses/", include("apps.expenses.urls")),
    path("api/v1/analytics/", include("apps.analytics.urls")),
    path("api/v1/core/", include("apps.core.urls")),
]
