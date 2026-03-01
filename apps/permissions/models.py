"""
Dynamic Permission System – scalable, per-membership custom permissions.

Architecture:
    AppPermission  →  master list of all possible permissions (seeded)
    MemberPermission  →  M2M: which membership has which permission

Owner always bypasses checks (has implicit ALL).
"""
from django.db import models
from apps.core.models import TimeStampedModel


class AppPermission(models.Model):
    """
    Master permission registry.  Seeded via data migration / management command.
    """

    codename = models.CharField(max_length=60, unique=True, db_index=True)
    label = models.CharField(max_length=120)
    description = models.TextField(blank=True, default="")
    module = models.CharField(
        max_length=30,
        db_index=True,
        help_text="Logical module: meals, expenses, analytics, members, flat",
    )

    class Meta:
        db_table = "app_permissions"
        ordering = ["module", "codename"]

    def __str__(self):
        return f"{self.module}:{self.codename}"


class MemberPermission(TimeStampedModel):
    """
    Per-membership permission assignment.
    Owner can assign any combination to any member.
    """

    membership = models.ForeignKey(
        "flats.FlatMembership",
        on_delete=models.CASCADE,
        related_name="permissions",
    )
    permission = models.ForeignKey(
        AppPermission,
        on_delete=models.CASCADE,
        related_name="assignments",
    )
    granted_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "member_permissions"
        unique_together = ("membership", "permission")
        indexes = [
            models.Index(fields=["membership", "permission"]),
        ]

    def __str__(self):
        return f"{self.membership} → {self.permission.codename}"


# ---------------------------------------------------------------------------
# Seed data – all available permissions
# ---------------------------------------------------------------------------
PERMISSION_SEED = [
    # Meals
    ("add_meal", "Add Meal Entry", "meals"),
    ("edit_meal", "Edit Meal Entry", "meals"),
    ("delete_meal", "Delete Meal Entry", "meals"),
    ("view_meals", "View Meal Table", "meals"),
    # Expenses
    ("add_expense", "Add Bazar Expense", "expenses"),
    ("edit_expense", "Edit Bazar Expense", "expenses"),
    ("delete_expense", "Delete Bazar Expense", "expenses"),
    ("view_expenses", "View Expenses", "expenses"),
    # Analytics
    ("view_analytics", "View Analytics Dashboard", "analytics"),
    ("export_report", "Export Reports", "analytics"),
    # Flat management
    ("edit_flat", "Edit Flat Details", "flat"),
    ("close_month", "Lock / Close Month", "flat"),
    ("reopen_month", "Reopen Closed Month", "flat"),
    # Members
    ("view_members", "View Member List", "members"),
    ("edit_other_users", "Edit Other Members", "members"),
    ("manage_permissions", "Manage Permissions", "members"),
    ("create_invite", "Create Invite Links", "members"),
]
