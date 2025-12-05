from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User, Tenant, Invitation
from .serializers import (
    UserSerializer, CustomTokenObtainPairSerializer,
    TenantSerializer, InvitationSerializer, AcceptInvitationSerializer
)

from django.template.loader import render_to_string
from djangoo.utils.html import strip_tags
from django.utils import timezone
from datetime import timedelta

from loguru import logger

from .tasks import send_invitation_email

class CreateTenantView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = TenantSerializer

    def perform_create(self, serializer):
        tenant = serializer.save()
        user = self.request.user
        if user.is_authenticated and user.is_superuser:
            tenant.owner = user
            tenant.save()
        return tenant
class InviteUserView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = InvitationSerializer

    def create(self, request, *args, **kwargs):
        if not request.user.tenant:
            return Response(
                {"error": "You must be part of a tenant to invite users."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.user.role not in ['owner', 'admin']:
            return Response(
                {"error": "You don't have permission to invite users."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        if (request.user.role == 'admin' and 
            serializer.validated_data['role'] in ['owner', 'admin']):
            return Response(
                {"error": "You can only invite users with lower privileges."},
                status=status.HTTP_403_FORBIDDEN
            )

        invitation = Invitation.objects.create(
            **serializer.validated_data,
            tenant=request.user.tenant,
            invited_by=request.user,
            expires_at=timezone.now() + timedelta(days=7)
        )

        try:
            send_invitation_email.delay(invitation.id)
            return Response(
                {"message": "Invitation sent successfully."},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            logger.error(f"Failed to send invitation email: {str(e)}", exc_info=True)
            return Response(
                {"error": "Failed to send invitation email. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
class AcceptInvitationView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = AcceptInvitationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            invitation = Invitation.objects.get(
                token=serializer.validated_data['token'],
                is_accepted=False
            )
        except Invitation.DoesNotExist:
            return Response(
                {"error": "Invalid or expired invitation."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if invitation.is_expired():
            return Response(
                {"error": "This invitation has expired."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create user
        user = User.objects.create_user(
            email=invitation.email,
            password=serializer.validated_data['password'],
            first_name=serializer.validated_data['first_name'],
            last_name=serializer.validated_data['last_name'],
            tenant=invitation.tenant,
            role=invitation.role,
            is_active=True
        )

        invitation.is_accepted = True
        invitation.save()

        return Response(
            {"message": "Account created successfully. You can now log in."},
            status=status.HTTP_201_CREATED
        )
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "message": "User registered successfully",
            "user_id": user.id,
            "email": user.email
        }, status=status.HTTP_201_CREATED)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'tenant': str(user.tenant_id) if user.tenant_id else None
        })
