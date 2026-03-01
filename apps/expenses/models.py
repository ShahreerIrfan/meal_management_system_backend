"""
Expense (Bazar) model.
"""
from django.conf import settings
from django.db import models
from apps.core.models import TimeStampedModel


class Expense(TimeStampedModel):
    """
    A single bazar / expense entry.
    """

    flat = models.ForeignKey(
        "flats.Flat", on_delete=models.CASCADE, related_name="expenses"
    )
    paid_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="expenses",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=500, blank=True, default="")
    date = models.DateField(db_index=True)

    class Meta:
        db_table = "expenses"
        indexes = [
            models.Index(fields=["flat", "date"]),
            models.Index(fields=["flat", "paid_by"]),
        ]
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.paid_by.full_name} | {self.date} | {self.amount}"


class AuditLog(TimeStampedModel):
    """
    Generic audit trail for important mutations.
    """

    flat = models.ForeignKey(
        "flats.Flat", on_delete=models.CASCADE, related_name="audit_logs"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=50, db_index=True)
    entity_type = models.CharField(max_length=50)
    entity_id = models.CharField(max_length=50, blank=True)
    details = models.JSONField(default=dict)

    class Meta:
        db_table = "audit_logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["flat", "action"]),
        ]

    def __str__(self):
        return f"[{self.action}] {self.entity_type}:{self.entity_id} by {self.user}"
