# from django.urls import path
# from rest_framework_simplejwt.views import TokenRefreshView
# from .views import (
#     FirebaseTokenExchangeView,
#     WorkspaceDetailView,
#     RotateInviteCodeView,
#     ValidateInviteCodeView,
#     UserProfileView,
#     TeamMembersView,
#     UploadAvatarView,
#     UploadTenantLogoView,
# )

# urlpatterns = [
#     # Auth & JWT Tokens
#     path('auth/firebase/', FirebaseTokenExchangeView.as_view(), name='auth_firebase'),
#     path('auth/jwt/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

#     # Users
#     path('users/me/', UserProfileView.as_view(), name='user_me'),
#     path('users/<str:user_id>/', UserProfileView.as_view(), name='user_detail_compat'),
#     path('users/<str:user_id>/avatar/', UploadAvatarView.as_view(), name='user_avatar_compat'),
#     path('users/team/', TeamMembersView.as_view(), name='team_members'),
#     path('users/avatar/', UploadAvatarView.as_view(), name='upload_avatar'),

#     # Workspace & Invitations
#     path('workspace/', WorkspaceDetailView.as_view(), name='workspace_detail'),
#     path('tenants/<str:tenant_id>/', WorkspaceDetailView.as_view(), name='tenant_detail_compat'),
#     path('workspace/logo/', UploadTenantLogoView.as_view(), name='upload_tenant_logo'),
#     path('workspace/rotate-invite/', RotateInviteCodeView.as_view(), name='rotate_invite_code'),
#     path('workspace/validate-invite/', ValidateInviteCodeView.as_view(), name='validate_invite_code'),
# ]

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    FirebaseTokenExchangeView,
    WorkspaceDetailView,
    RotateInviteCodeView,
    ValidateInviteCodeView,
    UserProfileView,
    TeamMembersView,
    UploadAvatarView,
    UploadTenantLogoView,
)

urlpatterns = [
    # Auth & Tokens
    path('auth/firebase/', FirebaseTokenExchangeView.as_view(), name='auth_firebase'),
    path('auth/jwt/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # User Profile Endpoints
    path('users/me/', UserProfileView.as_view(), name='user_me'),
    path('users/<str:user_id>/', UserProfileView.as_view(), name='user_detail_compat'),
    path('users/<str:user_id>/avatar/', UploadAvatarView.as_view(), name='user_avatar_compat'),
    path('users/avatar/', UploadAvatarView.as_view(), name='upload_avatar'),
    path('users/team/', TeamMembersView.as_view(), name='team_members'),

    # Workspace & Tenant Endpoints
    path('workspace/', WorkspaceDetailView.as_view(), name='workspace_detail'),
    path('tenants/<str:tenant_id>/', WorkspaceDetailView.as_view(), name='tenant_detail_compat'),
    path('workspace/logo/', UploadTenantLogoView.as_view(), name='upload_tenant_logo'),
    path('workspace/rotate-invite/', RotateInviteCodeView.as_view(), name='rotate_invite_code'),
    path('workspace/validate-invite/', ValidateInviteCodeView.as_view(), name='validate_invite_code'),
]