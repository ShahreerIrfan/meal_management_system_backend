"""
Analytics service – aggregated data for charts.
"""
from decimal import Decimal
from collections import defaultdict
from django.db.models import Sum, Value, DecimalField
from django.db.models.functions import Coalesce, TruncDate
from apps.meals.models import MealEntry, MonthlySummary
from apps.expenses.models import Expense
from apps.flats.models import Flat, FlatMembership


def meal_count_per_user(flat: Flat, year: int, month: int):
    """Bar chart data: { user_name: total_meals }"""
    qs = (
        MealEntry.objects.filter(flat=flat, date__year=year, date__month=month)
        .values("user__full_name")
        .annotate(total=Coalesce(Sum("meal_count"), Value(Decimal("0")), output_field=DecimalField()))
        .order_by("user__full_name")
    )
    return [{"name": r["user__full_name"], "meals": float(r["total"])} for r in qs]


def expense_share_per_user(flat: Flat, year: int, month: int):
    """Pie chart data: how much each user paid."""
    qs = (
        Expense.objects.filter(flat=flat, date__year=year, date__month=month)
        .values("paid_by__full_name")
        .annotate(total=Coalesce(Sum("amount"), Value(Decimal("0")), output_field=DecimalField()))
        .order_by("paid_by__full_name")
    )
    return [{"name": r["paid_by__full_name"], "amount": float(r["total"])} for r in qs]


def daily_meal_trend(flat: Flat, year: int, month: int):
    """Line chart data: total meals per day."""
    qs = (
        MealEntry.objects.filter(flat=flat, date__year=year, date__month=month)
        .values("date")
        .annotate(total=Coalesce(Sum("meal_count"), Value(Decimal("0")), output_field=DecimalField()))
        .order_by("date")
    )
    return [{"date": str(r["date"]), "meals": float(r["total"])} for r in qs]


def monthly_comparison(flat: Flat, year: int):
    """
    Compare month-by-month for a given year.
    Used for the monthly comparison chart.
    """
    summaries = MonthlySummary.objects.filter(flat=flat, year=year).order_by("month")
    return [
        {
            "month": s.month,
            "total_meals": float(s.total_meals),
            "total_expense": float(s.total_expense),
            "meal_rate": float(s.meal_rate),
        }
        for s in summaries
    ]
