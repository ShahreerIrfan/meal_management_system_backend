"""
Permission service layer – assign / revoke / check permissions.
"""
from typing import List, Set
from django.db import transaction
from apps.flats.models import FlatMembership
from .models import AppPermission, MemberPermission, PERMISSION_SEED


def seed_permissions():
    """Idempotent: create all master permissions from PERMISSION_SEED."""
    for codename, label, module in PERMISSION_SEED:
        AppPermission.objects.update_or_create(
            codename=codename,
            defaults={"label": label, "module": module},
        )


def assign_all_permissions(membership: FlatMembership, granted_by=None):
    """Give a membership every permission (used for owners)."""
    all_perms = AppPermission.objects.all()
    with transaction.atomic():
        for perm in all_perms:
            MemberPermission.objects.get_or_create(
                membership=membership,
                permission=perm,
                defaults={"granted_by": granted_by or membership.user},
            )


def set_permissions(
    membership: FlatMembership,
    codenames: List[str],
    granted_by=None,
):
    """
    Replace a member's permission set with the given codenames.
    Removes permissions not in the list, adds missing ones.
    """
    target_perms = set(
        AppPermission.objects.filter(codename__in=codenames).values_list("id", flat=True)
    )
    with transaction.atomic():
        # Remove old permissions not in target list
        MemberPermission.objects.filter(membership=membership).exclude(
            permission_id__in=target_perms
        ).delete()
        # Add new permissions
        existing = set(
            MemberPermission.objects.filter(membership=membership).values_list(
                "permission_id", flat=True
            )
        )
        to_create = target_perms - existing
        MemberPermission.objects.bulk_create(
            [
                MemberPermission(
                    membership=membership,
                    permission_id=pid,
                    granted_by=granted_by,
                )
                for pid in to_create
            ]
        )


def get_permission_codenames(membership: FlatMembership) -> Set[str]:
    """Return set of permission codenames for a membership."""
    if membership.is_owner:
        return set(AppPermission.objects.values_list("codename", flat=True))
    return set(
        MemberPermission.objects.filter(membership=membership).values_list(
            "permission__codename", flat=True
        )
    )


def has_permission(membership: FlatMembership, codename: str) -> bool:
    """Check if membership has a specific permission."""
    if membership.is_owner:
        return True
    return MemberPermission.objects.filter(
        membership=membership, permission__codename=codename
    ).exists()
