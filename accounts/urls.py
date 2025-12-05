from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView, 
    CustomTokenObtainPairView, 
    UserProfileView, 
    CreateTenantView,
    ListTenantsView,
    ListUsersView,
    InviteUserView, 
    AcceptInvitationView,
    UpdateUserView,
    DeleteUserView
)
app_name = 'accounts'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('profile/', UserProfileView.as_view(), name='profile'),
    path('list/users', ListUsersView.as_view(), name='list_users'),

    path('create/tenant', CreateTenantView.as_view(), name='create_tenant'),
    path('update/user/<str:pk>', UpdateUserView.as_view(), name='update_user'),
    path('delete/user/<str:pk>', DeleteUserView.as_view(), name='delete_user'),
    path('list/tenants', ListTenantsView.as_view(), name='list_tenant'),
    path('invite/user', InviteUserView.as_view(), name='invite_user'),
    path('accept/invitation', AcceptInvitationView.as_view(), name='accept_invitaion')

]