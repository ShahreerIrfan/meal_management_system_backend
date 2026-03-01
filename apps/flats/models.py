"""
Flat, FlatMembership, InviteToken, MemberMonthStatus models.
"""
import uuid
from datetime import timedelta
from django.conf import settings
from django.db import models
from django.utils import timezone
from apps.core.models import TimeStampedModel


class Flat(TimeStampedModel):
    """A flat / household unit – the tenant in the SaaS model."""

    name = models.CharField(max_length=200)
    address = models.TextField(blank=True, default="")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_flats",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "flats"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class FlatMembership(TimeStampedModel):
    """
    M2M through table: User ↔ Flat.
    Stores role + active status.  Permissions stored in permissions app.
    """

    class Role(models.TextChoices):
        OWNER = "owner", "Flat Owner"
        MEMBER = "member", "Member"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    flat = models.ForeignKey(Flat, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.MEMBER)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "flat_memberships"
        unique_together = ("user", "flat")
        indexes = [
            models.Index(fields=["flat", "is_active"]),
        ]

    def __str__(self):
        return f"{self.user.full_name} @ {self.flat.name} ({self.role})"

    @property
    def is_owner(self):
        return self.role == self.Role.OWNER


class InviteToken(TimeStampedModel):
    """
    Invite link token – unique, expires, belongs to a specific flat.
    Carries a set of permissions to be assigned to users who join.
    """

    flat = models.ForeignKey(Flat, on_delete=models.CASCADE, related_name="invites")
    token = models.CharField(max_length=64, unique=True, db_index=True, default="")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_invites",
    )
    expires_at = models.DateTimeField()
    max_uses = models.PositiveIntegerField(default=1)
    times_used = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    granted_permissions = models.ManyToManyField(
        "permissions.AppPermission",
        blank=True,
        related_name="invite_tokens",
        help_text="Permissions to assign to members who join via this invite.",
    )

    class Meta:
        db_table = "invite_tokens"
        indexes = [
            models.Index(fields=["token"]),
            models.Index(fields=["flat", "is_active"]),
        ]

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = uuid.uuid4().hex
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(
                days=settings.INVITE_LINK_EXPIRY_DAYS
            )
        super().save(*args, **kwargs)

    @property
    def is_valid(self):
        return (
            self.is_active
            and self.times_used < self.max_uses
            and timezone.now() < self.expires_at
        )

    def __str__(self):
        return f"Invite {self.token[:8]}… for {self.flat.name}"


class MemberMonthStatus(TimeStampedModel):
    """
    Tracks whether a member is active for a specific month.
    Allows temporarily disabling a member (e.g. they won't eat meals this month)
    or setting a specific start/end date within the month.

    If no record exists for a member/month → considered ACTIVE (default).
    """

    membership = models.ForeignKey(
        FlatMembership, on_delete=models.CASCADE, related_name="month_statuses"
    )
    flat = models.ForeignKey(Flat, on_delete=models.CASCADE, related_name="member_month_statuses")
    year = models.PositiveIntegerField()
    month = models.PositiveIntegerField()  # 1-12
    is_active = models.BooleanField(
        default=True,
        help_text="If False, member is fully off for this month",
    )
    active_from = models.DateField(
        null=True, blank=True,
        help_text="If set, member is only active from this date onwards (within the month)",
    )
    active_until = models.DateField(
        null=True, blank=True,
        help_text="If set, member is only active until this date (within the month)",
    )
    note = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        db_table = "member_month_status"
        unique_together = ("membership", "year", "month")
        indexes = [
            models.Index(fields=["flat", "year", "month"]),
        ]

    def __str__(self):
        status_str = "Active" if self.is_active else "Inactive"
        return f"{self.membership.user.full_name} | {self.year}-{self.month:02d} | {status_str}"
