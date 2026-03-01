"""
Analytics endpoints – aggregated data for frontend charts.
"""
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.permissions.guards import flat_permission_required
from apps.meals.serializers import MonthYearSerializer
from . import services


class MealCountPerUserView(APIView):
    """GET /analytics/meal-per-user/?year=2026&month=2"""

    permission_classes = [
        permissions.IsAuthenticated,
        flat_permission_required("view_analytics"),
    ]

    def get(self, request):
        p = MonthYearSerializer(data=request.query_params)
        p.is_valid(raise_exception=True)
        data = services.meal_count_per_user(
            request.flat, p.validated_data["year"], p.validated_data["month"]
        )
        return Response({"success": True, "data": data})


class ExpenseShareView(APIView):
    """GET /analytics/expense-share/?year=2026&month=2"""

    permission_classes = [
        permissions.IsAuthenticated,
        flat_permission_required("view_analytics"),
    ]

    def get(self, request):
        p = MonthYearSerializer(data=request.query_params)
        p.is_valid(raise_exception=True)
        data = services.expense_share_per_user(
            request.flat, p.validated_data["year"], p.validated_data["month"]
        )
        return Response({"success": True, "data": data})


class DailyMealTrendView(APIView):
    """GET /analytics/daily-meals/?year=2026&month=2"""

    permission_classes = [
        permissions.IsAuthenticated,
        flat_permission_required("view_analytics"),
    ]

    def get(self, request):
        p = MonthYearSerializer(data=request.query_params)
        p.is_valid(raise_exception=True)
        data = services.daily_meal_trend(
            request.flat, p.validated_data["year"], p.validated_data["month"]
        )
        return Response({"success": True, "data": data})


class MonthlyComparisonView(APIView):
    """GET /analytics/monthly-comparison/?year=2026"""

    permission_classes = [
        permissions.IsAuthenticated,
        flat_permission_required("view_analytics"),
    ]

    def get(self, request):
        year = int(request.query_params.get("year", 2026))
        data = services.monthly_comparison(request.flat, year)
        return Response({"success": True, "data": data})
