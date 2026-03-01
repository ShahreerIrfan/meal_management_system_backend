"""
Expense views – CRUD + auto-recalculation.
"""
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from apps.permissions.guards import flat_permission_required
from apps.core.models import ActivityLog
from apps.meals.calculation_engine import recalculate_month, is_month_locked
from .models import Expense, AuditLog
from .serializers import ExpenseSerializer, ExpenseCreateSerializer, AuditLogSerializer


class ExpenseListCreateView(generics.ListCreateAPIView):
    """
    GET   /expenses/?year=2026&month=2   – list expenses
    POST  /expenses/                      – create expense
    """

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ExpenseCreateSerializer
        return ExpenseSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated(), flat_permission_required("add_expense")()]
        return [permissions.IsAuthenticated(), flat_permission_required("view_expenses")()]

    def get_queryset(self):
        qs = Expense.objects.filter(flat=self.request.flat).select_related("paid_by")
        year = self.request.query_params.get("year")
        month = self.request.query_params.get("month")
        if year and month:
            qs = qs.filter(date__year=int(year), date__month=int(month))
        return qs

    def perform_create(self, serializer):
        expense = serializer.save(flat=self.request.flat)
        # Recalculate the affected month
        recalculate_month(self.request.flat, expense.date.year, expense.date.month)
        # Audit
        AuditLog.objects.create(
            flat=self.request.flat,
            user=self.request.user,
            action="create_expense",
            entity_type="Expense",
            entity_id=str(expense.id),
            details={"amount": str(expense.amount), "date": str(expense.date)},
        )
        ActivityLog.log(
            user=self.request.user,
            flat=self.request.flat,
            action=ActivityLog.ActionType.EXPENSE_ADD,
            description=f"Added expense of {expense.amount} on {expense.date}",
            metadata={"expense_id": str(expense.id), "amount": str(expense.amount), "date": str(expense.date)},
            request=self.request,
        )


class ExpenseDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET / PUT / PATCH / DELETE  /expenses/<id>/
    """

    serializer_class = ExpenseSerializer

    def get_permissions(self):
        if self.request.method in ("PUT", "PATCH"):
            return [permissions.IsAuthenticated(), flat_permission_required("edit_expense")()]
        if self.request.method == "DELETE":
            return [permissions.IsAuthenticated(), flat_permission_required("delete_expense")()]
        return [permissions.IsAuthenticated(), flat_permission_required("view_expenses")()]

    def get_queryset(self):
        return Expense.objects.filter(flat=self.request.flat).select_related("paid_by")

    def perform_update(self, serializer):
        expense = serializer.save()
        recalculate_month(self.request.flat, expense.date.year, expense.date.month)
        ActivityLog.log(
            user=self.request.user,
            flat=self.request.flat,
            action=ActivityLog.ActionType.EXPENSE_UPDATE,
            description=f"Updated expense {expense.id} (amount: {expense.amount})",
            metadata={"expense_id": str(expense.id), "amount": str(expense.amount), "date": str(expense.date)},
            request=self.request,
        )

    def perform_destroy(self, instance):
        year, month = instance.date.year, instance.date.month
        expense_id = str(instance.id)
        expense_amount = str(instance.amount)
        expense_date = str(instance.date)
        AuditLog.objects.create(
            flat=self.request.flat,
            user=self.request.user,
            action="delete_expense",
            entity_type="Expense",
            entity_id=expense_id,
            details={"amount": expense_amount, "date": expense_date},
        )
        instance.delete()
        recalculate_month(self.request.flat, year, month)
        ActivityLog.log(
            user=self.request.user,
            flat=self.request.flat,
            action=ActivityLog.ActionType.EXPENSE_DELETE,
            description=f"Deleted expense {expense_id} (amount: {expense_amount})",
            metadata={"expense_id": expense_id, "amount": expense_amount, "date": expense_date},
            request=self.request,
        )


class AuditLogListView(generics.ListAPIView):
    """GET /expenses/audit/ – audit trail for the flat."""

    serializer_class = AuditLogSerializer

    def get_queryset(self):
        return AuditLog.objects.filter(flat=self.request.flat).select_related("user")[:200]
