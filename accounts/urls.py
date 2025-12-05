from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView, 
    CustomTokenObtainPairView, 
    UserProfileView, 
    CreateTenantView,
    InviteUserView
)
app_name = 'accounts'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', UserProfileView.as_view(), name='profile'),

    path('create/tenant', CreateTenantView.as_view(), name='create_tenant'),
    path('invite/user', InviteUserView.as_view(), name='invite_user'),
    path('accept/invitation', AcceptInvitationView.as_view(), name='accept_invitaion')

]