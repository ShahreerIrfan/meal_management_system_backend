"""
DRF permission guard classes.
Used in views: permission_classes = [IsAuthenticated, HasFlatPermission("add_meal")]
"""
from rest_framework.permissions import BasePermission
from apps.permissions.services import has_permission as check_perm


class IsOwner(BasePermission):
    """Only allows flat owners."""

    def has_permission(self, request, view):
        return (
            request.membership is not None
            and request.membership.is_owner
        )


class HasFlatPermission(BasePermission):
    """
    Factory-style permission class.

    Usage in view:
        permission_classes = [IsAuthenticated, HasFlatPermission("add_meal")]

    Or dynamically:
        def get_permissions(self):
            return [IsAuthenticated(), HasFlatPermission("add_meal")]
    """

    def __init__(self, codename: str = ""):
        self.codename = codename

    def has_permission(self, request, view):
        if not request.membership:
            return False
        if not self.codename:
            # Just check that user belongs to a flat
            return True
        return check_perm(request.membership, self.codename)


class HasAnyFlatPermission(BasePermission):
    """Pass if membership has ANY of the listed codenames."""

    def __init__(self, *codenames: str):
        self.codenames = codenames

    def has_permission(self, request, view):
        if not request.membership:
            return False
        return any(
            check_perm(request.membership, c) for c in self.codenames
        )


def flat_permission_required(codename: str):
    """
    Decorator-like helper to build permission class inline.

    Usage:
        permission_classes = [IsAuthenticated, flat_permission_required("add_meal")]
    """
    class _Perm(BasePermission):
        def has_permission(self, request, view):
            if not request.membership:
                return False
            return check_perm(request.membership, codename)
    _Perm.__name__ = f"FlatPerm_{codename}"
    return _Perm
