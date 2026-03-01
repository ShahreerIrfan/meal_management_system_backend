"""
Permission serializers.
"""
from rest_framework import serializers
from .models import AppPermission, MemberPermission


class AppPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppPermission
        fields = ["id", "codename", "label", "description", "module"]


class MemberPermissionSerializer(serializers.ModelSerializer):
    codename = serializers.CharField(source="permission.codename", read_only=True)
    label = serializers.CharField(source="permission.label", read_only=True)
    module = serializers.CharField(source="permission.module", read_only=True)

    class Meta:
        model = MemberPermission
        fields = ["id", "codename", "label", "module", "created_at"]


class SetPermissionsSerializer(serializers.Serializer):
    """Payload for setting a member's permissions."""

    membership_id = serializers.UUIDField()
    codenames = serializers.ListField(child=serializers.CharField(), allow_empty=True)
