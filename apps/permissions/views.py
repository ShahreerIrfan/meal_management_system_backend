"""
Permission views – list all permissions, get member's perms, set perms.
"""
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.flats.models import FlatMembership
from apps.permissions.guards import IsOwner
from .models import AppPermission, MemberPermission
from .serializers import (
    AppPermissionSerializer,
    MemberPermissionSerializer,
    SetPermissionsSerializer,
)
from .services import set_permissions, get_permission_codenames


class AllPermissionsView(generics.ListAPIView):
    """List all available permissions (master list)."""

    serializer_class = AppPermissionSerializer
    queryset = AppPermission.objects.all()


class MemberPermissionsView(APIView):
    """Get permissions for a specific membership."""

    def get(self, request, membership_id):
        try:
            membership = FlatMembership.objects.get(
                id=membership_id, flat=request.flat
            )
        except FlatMembership.DoesNotExist:
            return Response(
                {"success": False, "errors": {"detail": "Membership not found"}},
                status=status.HTTP_404_NOT_FOUND,
            )
        codenames = get_permission_codenames(membership)
        return Response({"success": True, "codenames": sorted(codenames)})


class SetPermissionsView(APIView):
    """Owner sets permissions for a member."""

    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def post(self, request):
        serializer = SetPermissionsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            membership = FlatMembership.objects.get(
                id=serializer.validated_data["membership_id"],
                flat=request.flat,
            )
        except FlatMembership.DoesNotExist:
            return Response(
                {"success": False, "errors": {"detail": "Membership not found"}},
                status=status.HTTP_404_NOT_FOUND,
            )

        if membership.is_owner:
            return Response(
                {"success": False, "errors": {"detail": "Cannot modify owner permissions"}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        set_permissions(
            membership,
            serializer.validated_data["codenames"],
            granted_by=request.user,
        )
        codenames = get_permission_codenames(membership)
        return Response(
            {"success": True, "codenames": sorted(codenames), "message": "Permissions updated."}
        )


class MyPermissionsView(APIView):
    """Current user's permissions in the active flat."""

    def get(self, request):
        if not request.membership:
            return Response({"success": True, "codenames": []})
        codenames = get_permission_codenames(request.membership)
        return Response({"success": True, "codenames": sorted(codenames)})
