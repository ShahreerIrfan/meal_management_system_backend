"""
=================================================================
  CALCULATION ENGINE  –  Isolated service layer
=================================================================

All monetary / meal calculations live here.
NEVER mix this logic into serializers or views.

Formulas:
    total_meals     = SUM(meal_count) for flat in month
    total_expense   = SUM(expense.amount) for flat in month
    meal_rate       = total_expense / total_meals   (0 if no meals)
    individual_cost = user_meals × meal_rate
    balance         = total_paid − individual_cost
        balance > 0  →  user receives money
        balance < 0  →  user must pay

Optimisation:
    - Only recalculates the AFFECTED month (via flat + year + month).
    - Uses aggregation queries – no Python-level loops over rows.
    - Results are persisted in MonthlySummary (cache table).
=================================================================
"""
from decimal import Decimal
from typing import Dict, List, Optional

from django.db.models import Sum, F, Value, DecimalField
from django.db.models.functions import Coalesce
from django.utils import timezone

from apps.meals.models import MealEntry, MonthlySummary
from apps.expenses.models import Expense
from apps.flats.models import Flat, FlatMembership


# -------------------------------------------------------------------
#  Core recalculation  (called after every meal / expense mutation)
# -------------------------------------------------------------------

def recalculate_month(flat: Flat, year: int, month: int) -> MonthlySummary:
    """
    Recalculate totals for a single flat-month.
    Creates / updates the MonthlySummary row.
    Returns the updated summary.
    """
    total_meals = (
        MealEntry.objects.filter(flat=flat, date__year=year, date__month=month)
        .aggregate(
            total=Coalesce(Sum("meal_count"), Value(Decimal("0")), output_field=DecimalField())
        )["total"]
    )

    total_expense = (
        Expense.objects.filter(flat=flat, date__year=year, date__month=month)
        .aggregate(
            total=Coalesce(Sum("amount"), Value(Decimal("0")), output_field=DecimalField())
        )["total"]
    )

    meal_rate = (total_expense / total_meals) if total_meals > 0 else Decimal("0")

    summary, _ = MonthlySummary.objects.update_or_create(
        flat=flat,
        year=year,
        month=month,
        defaults={
            "total_meals": total_meals,
            "total_expense": total_expense,
            "meal_rate": meal_rate.quantize(Decimal("0.01")),
        },
    )
    return summary


# -------------------------------------------------------------------
#  Per-user breakdown for a month
# -------------------------------------------------------------------

def get_user_balances(flat: Flat, year: int, month: int) -> List[Dict]:
    """
    Returns a list of dicts – one per flat member:
    {
        "user_id": uuid,
        "full_name": str,
        "total_meals": Decimal,
        "total_paid": Decimal,
        "individual_cost": Decimal,
        "balance": Decimal,      # positive = receives, negative = owes
    }
    """
    summary = recalculate_month(flat, year, month)
    meal_rate = summary.meal_rate

    members = get_grid_members(flat, year, month)

    # Aggregate meals per user
    user_meals = dict(
        MealEntry.objects.filter(flat=flat, date__year=year, date__month=month)
        .values("user_id")
        .annotate(total=Coalesce(Sum("meal_count"), Value(Decimal("0")), output_field=DecimalField()))
        .values_list("user_id", "total")
    )

    # Aggregate amount paid per user
    user_paid = dict(
        Expense.objects.filter(flat=flat, date__year=year, date__month=month)
        .values("paid_by_id")
        .annotate(total=Coalesce(Sum("amount"), Value(Decimal("0")), output_field=DecimalField()))
        .values_list("paid_by_id", "total")
    )

    results = []
    for m in members:
        meals = user_meals.get(m.user_id, Decimal("0"))
        paid = user_paid.get(m.user_id, Decimal("0"))
        cost = (meals * meal_rate).quantize(Decimal("0.01"))
        balance = (paid - cost).quantize(Decimal("0.01"))
        results.append(
            {
                "user_id": str(m.user_id),
                "full_name": m.user.full_name,
                "total_meals": meals,
                "total_paid": paid,
                "individual_cost": cost,
                "balance": balance,
            }
        )
    return results


# -------------------------------------------------------------------
#  Quick summary for dashboard header
# -------------------------------------------------------------------

def get_month_summary(flat: Flat, year: int, month: int) -> Dict:
    summary = recalculate_month(flat, year, month)
    return {
        "year": year,
        "month": month,
        "total_meals": summary.total_meals,
        "total_expense": summary.total_expense,
        "meal_rate": summary.meal_rate,
        "is_locked": summary.is_locked,
    }


# -------------------------------------------------------------------
#  Lock / Unlock month
# -------------------------------------------------------------------

def lock_month(flat: Flat, year: int, month: int, user) -> MonthlySummary:
    summary = recalculate_month(flat, year, month)
    summary.is_locked = True
    summary.locked_by = user
    summary.locked_at = timezone.now()
    summary.save(update_fields=["is_locked", "locked_by", "locked_at", "updated_at"])
    return summary


def unlock_month(flat: Flat, year: int, month: int) -> MonthlySummary:
    summary, _ = MonthlySummary.objects.get_or_create(
        flat=flat, year=year, month=month
    )
    summary.is_locked = False
    summary.locked_by = None
    summary.locked_at = None
    summary.save(update_fields=["is_locked", "locked_by", "locked_at", "updated_at"])
    return summary


def get_grid_members(flat: Flat, year: int, month: int):
    """
    Return memberships to display as columns for the given month.
    Includes all active members PLUS any inactive members who have
    meal entries or expenses in that month.
    """
    active = FlatMembership.objects.filter(
        flat=flat, is_active=True
    ).select_related("user")

    # User IDs that have meal entries this month
    users_with_meals = set(
        MealEntry.objects.filter(
            flat=flat, date__year=year, date__month=month
        ).values_list("user_id", flat=True)
    )
    # User IDs that have expenses this month
    users_with_expenses = set(
        Expense.objects.filter(
            flat=flat, date__year=year, date__month=month
        ).values_list("paid_by_id", flat=True)
    )
    users_with_data = users_with_meals | users_with_expenses

    active_user_ids = set(active.values_list("user_id", flat=True))
    inactive_with_data_ids = users_with_data - active_user_ids

    if not inactive_with_data_ids:
        return active

    inactive_with_data = FlatMembership.objects.filter(
        flat=flat, user_id__in=inactive_with_data_ids
    ).select_related("user")

    # Combine querysets
    combined_ids = [m.id for m in active] + [m.id for m in inactive_with_data]
    return FlatMembership.objects.filter(id__in=combined_ids).select_related("user").order_by("user__full_name")


def is_month_locked(flat: Flat, year: int, month: int) -> bool:
    try:
        return MonthlySummary.objects.get(flat=flat, year=year, month=month).is_locked
    except MonthlySummary.DoesNotExist:
        return False
