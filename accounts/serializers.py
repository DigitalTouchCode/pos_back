from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Branch, Invitation, Tenant

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "password",
            "role",
            "first_name",
            "last_name",
            "tenant",
        )
        extra_kwargs = {
            "password": {"write_only": True, "min_length": 5},
            "tenant": {"read_only": True},
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data.update(
            {
                "user": {
                    "id": self.user.id,
                    "email": self.user.email,
                    "role": self.user.role,
                    "first_name": self.user.first_name,
                    "last_name": self.user.last_name,
                }
            }
        )
        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["role"] = user.role
        return token


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ["id", "name", "domain", "is_active"]
        read_only_fields = ["owner", "is_active"]


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ["id", "name", "tenant", "is_active"]
        read_only_fields = ["is_active"]


class InvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = ["email", "role", "branch"]
        extra_kwargs = {
            "email": {"required": True},
            "role": {"required": True},
            "branch": {"required": True},
        }


class AcceptInvitationSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    password = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
