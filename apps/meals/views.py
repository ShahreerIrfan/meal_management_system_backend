"""
Meal views – grid read, cell-level PATCH (auto-save), summary, lock/unlock.
"""
from datetime import date as dt_date
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.permissions.guards import HasFlatPermission, flat_permission_required
from apps.core.models import ActivityLog
from apps.flats.models import FlatMembership
from apps.flats.serializers import FlatMembershipSerializer
from .models import MealEntry
from .serializers import (
    MealCellUpdateSerializer,
    MealEntrySerializer,
    MonthYearSerializer,
    LockMonthSerializer,
)
from .calculation_engine import (
    recalculate_month,
    get_user_balances,
    get_month_summary,
    get_grid_members,
    lock_month,
    unlock_month,
    is_month_locked,
)


class MealGridView(APIView):
    """
    GET  /meals/grid/?year=2026&month=2
    Returns all meal entries for the flat in the given month,
    plus the calculated summary.
    """
    permission_classes = [
        permissions.IsAuthenticated,
        flat_permission_required("view_meals"),
    ]

    def get(self, request):
        params = MonthYearSerializer(data=request.query_params)
        params.is_valid(raise_exception=True)
        year = params.validated_data["year"]
        month = params.validated_data["month"]

        entries = (
            MealEntry.objects.filter(
                flat=request.flat, date__year=year, date__month=month
            )
            .select_related("user")
            .order_by("date", "user__full_name")
        )
        summary = get_month_summary(request.flat, year, month)
        balances = get_user_balances(request.flat, year, month)
        grid_members = get_grid_members(request.flat, year, month)

        return Response(
            {
                "success": True,
                "entries": MealEntrySerializer(entries, many=True).data,
                "summary": summary,
                "balances": balances,
                "members": FlatMembershipSerializer(grid_members, many=True).data,
            }
        )


class MealCellUpdateView(APIView):
    """
    PATCH  /meals/cell/
    Auto-save a single cell.  Returns recalculated summary.
    """
    permission_classes = [
        permissions.IsAuthenticated,
        flat_permission_required("add_meal"),
    ]

    def patch(self, request):
        serializer = MealCellUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data

        year, month = d["date"].year, d["date"].month
        if is_month_locked(request.flat, year, month):
            return Response(
                {"success": False, "errors": {"detail": "Month is locked."}},
                status=status.HTTP_403_FORBIDDEN,
            )

        entry, created = MealEntry.objects.update_or_create(
            flat=request.flat,
            user_id=d["user_id"],
            date=d["date"],
            defaults={"meal_count": d["meal_count"]},
        )

        ActivityLog.log(
            user=request.user,
            flat=request.flat,
            action=ActivityLog.ActionType.MEAL_ADD if created else ActivityLog.ActionType.MEAL_UPDATE,
            description=f"{'Added' if created else 'Updated'} meal entry for {d['date']} (count: {d['meal_count']})",
            metadata={"user_id": str(d["user_id"]), "date": str(d["date"]), "meal_count": str(d["meal_count"])},
            request=request,
        )

        # Recalculate only the affected month
        summary = get_month_summary(request.flat, year, month)
        balances = get_user_balances(request.flat, year, month)

        return Response(
            {
                "success": True,
                "entry": MealEntrySerializer(entry).data,
                "summary": summary,
                "balances": balances,
            }
        )


class MonthSummaryView(APIView):
    """
    GET  /meals/summary/?year=2026&month=2
    """

    def get(self, request):
        params = MonthYearSerializer(data=request.query_params)
        params.is_valid(raise_exception=True)
        year = params.validated_data["year"]
        month = params.validated_data["month"]

        summary = get_month_summary(request.flat, year, month)
        balances = get_user_balances(request.flat, year, month)

        return Response({"success": True, "summary": summary, "balances": balances})


class LockMonthView(APIView):
    """POST /meals/lock-month/"""

    permission_classes = [
        permissions.IsAuthenticated,
        flat_permission_required("close_month"),
    ]

    def post(self, request):
        ser = LockMonthSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        summary = lock_month(
            request.flat,
            ser.validated_data["year"],
            ser.validated_data["month"],
            request.user,
        )
        ActivityLog.log(
            user=request.user,
            flat=request.flat,
            action=ActivityLog.ActionType.MONTH_LOCK,
            description=f"Locked month {ser.validated_data['year']}-{ser.validated_data['month']:02d}",
            metadata={"year": ser.validated_data["year"], "month": ser.validated_data["month"]},
            request=request,
        )
        return Response(
            {"success": True, "message": "Month locked.", "is_locked": summary.is_locked}
        )


class UnlockMonthView(APIView):
    """POST /meals/unlock-month/"""

    permission_classes = [
        permissions.IsAuthenticated,
        flat_permission_required("reopen_month"),
    ]

    def post(self, request):
        ser = LockMonthSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        summary = unlock_month(
            request.flat,
            ser.validated_data["year"],
            ser.validated_data["month"],
        )
        ActivityLog.log(
            user=request.user,
            flat=request.flat,
            action=ActivityLog.ActionType.MONTH_UNLOCK,
            description=f"Unlocked month {ser.validated_data['year']}-{ser.validated_data['month']:02d}",
            metadata={"year": ser.validated_data["year"], "month": ser.validated_data["month"]},
            request=request,
        )
        return Response(
            {"success": True, "message": "Month unlocked.", "is_locked": summary.is_locked}
        )
