"""
Shared base model and utilities used across all apps.
"""
import uuid
from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    """Abstract base model with created/updated timestamps."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class ActivityLog(models.Model):
    """
    Activity log for tracking user actions across the application.
    Records who did what, when, and in which flat.
    """

    class ActionType(models.TextChoices):
        # Auth
        LOGIN = "login", "Logged in"
        LOGOUT = "logout", "Logged out"
        REGISTER = "register", "Registered"
        # Meals
        MEAL_ADD = "meal_add", "Added meal entry"
        MEAL_UPDATE = "meal_update", "Updated meal entry"
        MONTH_LOCK = "month_lock", "Locked month"
        MONTH_UNLOCK = "month_unlock", "Unlocked month"
        # Expenses
        EXPENSE_ADD = "expense_add", "Added expense"
        EXPENSE_UPDATE = "expense_update", "Updated expense"
        EXPENSE_DELETE = "expense_delete", "Deleted expense"
        # Members
        MEMBER_INVITE = "member_invite", "Created invite link"
        MEMBER_JOIN = "member_join", "Joined flat"
        MEMBER_REMOVE = "member_remove", "Removed member"
        MEMBER_STATUS = "member_status", "Updated member month status"
        # Permissions
        PERMISSION_UPDATE = "permission_update", "Updated permissions"
        # Flat
        FLAT_UPDATE = "flat_update", "Updated flat details"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activity_logs",
    )
    flat = models.ForeignKey(
        "flats.Flat",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="activity_logs",
    )
    action = models.CharField(max_length=30, choices=ActionType.choices)
    description = models.TextField(blank=True, default="")
    metadata = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "activity_logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["flat", "-created_at"]),
            models.Index(fields=["action", "-created_at"]),
        ]

    def __str__(self):
        user_name = self.user.full_name if self.user else "System"
        return f"{user_name} — {self.get_action_display()} — {self.created_at}"

    @classmethod
    def log(cls, user, flat, action, description="", metadata=None, request=None):
        """Convenience method to create a log entry."""
        ip = None
        if request:
            ip = request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip()
            if not ip:
                ip = request.META.get("REMOTE_ADDR")
        return cls.objects.create(
            user=user,
            flat=flat,
            action=action,
            description=description,
            metadata=metadata or {},
            ip_address=ip,
        )
