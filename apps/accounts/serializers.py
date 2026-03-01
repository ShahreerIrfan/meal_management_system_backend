"""
Account serializers – registration, login, profile.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.flats.models import Flat, FlatMembership

User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    """
    Owner registration – creates User + Flat + Membership in one shot.
    """
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)
    full_name = serializers.CharField(max_length=150)
    flat_name = serializers.CharField(max_length=200)
    flat_address = serializers.CharField(max_length=500, required=False, default="")

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already in use.")
        return value

    def create(self, validated_data):
        from apps.permissions.services import assign_all_permissions

        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            full_name=validated_data["full_name"],
        )
        flat = Flat.objects.create(
            name=validated_data["flat_name"],
            address=validated_data.get("flat_address", ""),
            owner=user,
        )
        membership = FlatMembership.objects.create(
            user=user,
            flat=flat,
            role=FlatMembership.Role.OWNER,
            is_active=True,
        )
        # Owner gets all permissions
        assign_all_permissions(membership)
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "full_name", "phone", "avatar", "created_at"]
        read_only_fields = ["id", "email", "created_at"]


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(min_length=8, write_only=True)
