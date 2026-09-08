
import logging
from pathlib import Path
# accounts/views.py
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings

import firebase_admin
from firebase_admin import auth, credentials
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Tenant, User, generate_invite_code
from .serializers import TeamMemberSerializer, TenantSerializer, UserProfileSerializer

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# Safe Firebase Admin Initialization
# ------------------------------------------------------------------------------
if not firebase_admin._apps:
    try:
        cert_path = Path(settings.BASE_DIR) / "firebase-service-account.json"
        if not cert_path.exists():
            cert_path = Path("firebase-service-account.json")

        cred = credentials.Certificate(str(cert_path))
        firebase_admin.initialize_app(cred)
        logger.info("✅ [Firebase Admin] Initialized successfully.")
    except Exception as e:
        logger.error(f"❌ [Firebase Admin] Initialization failed: {e}")


# ==============================================================================
# 1. AUTHENTICATION & ONBOARDING
# ==============================================================================
class FirebaseTokenExchangeView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        id_token = request.data.get("id_token")
        tenant_invite_code = request.data.get("tenant_invite_code")

        if not id_token:
            return Response(
                {"error": "id_token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            decoded_token = auth.verify_id_token(id_token, clock_skew_seconds=60)
            phone_number = decoded_token.get('phone_number')

            if not phone_number:
                return Response(
                    {"error": "Invalid token: phone number claim missing in Firebase ID token."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            with transaction.atomic():
                user = (
                    User.objects.select_related('tenant', 'invited_by')
                    .filter(phone_number=phone_number)
                    .first()
                )
                is_new_user = False

                if not user:
                    is_new_user = True

                    if tenant_invite_code:
                        tenant = Tenant.objects.filter(
                            invite_code=tenant_invite_code.strip().upper(),
                            is_active=True,
                            is_deleted=False,
                        ).first()

                        if not tenant:
                            return Response(
                                {"error": "Invalid or expired agency invite code."},
                                status=status.HTTP_404_NOT_FOUND,
                            )

                        user = User.objects.create_user(
                            phone_number=phone_number,
                            whatsapp_number=phone_number,
                            tenant=tenant,
                            role=User.RoleChoices.AGENT,
                            invited_by=tenant.owner,
                        )
                    else:
                        user = User.objects.create_user(
                            phone_number=phone_number,
                            whatsapp_number=phone_number,
                            role=User.RoleChoices.OWNER,
                        )
                        tenant = Tenant.objects.create(
                            name="My Real Estate Agency",
                            owner=user,
                            official_phone=phone_number,
                        )
                        user.tenant = tenant
                        user.save(update_fields=['tenant'])
                else:
                    user.last_login_at = timezone.now()
                    user.save(update_fields=['last_login_at'])

                    if not user.full_name or not user.full_name.strip():
                        is_new_user = True

                refresh = RefreshToken.for_user(user)

                return Response(
                    {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                        'is_new_user': is_new_user,
                        'user': UserProfileSerializer(user).data,
                        'tenant': TenantSerializer(user.tenant).data if user.tenant else None,
                    },
                    status=status.HTTP_200_OK,
                )

        except auth.ExpiredIdTokenError:
            return Response(
                {"error": "Firebase token has expired. Please re-request OTP."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except auth.InvalidIdTokenError as e:
            return Response(
                {"error": f"Invalid Firebase token: {str(e)}"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except Exception as e:
            logger.exception("Auth Token Exchange Error")
            return Response(
                {"error": f"Authentication failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# ==============================================================================
# 2. WORKSPACE / TENANT MANAGEMENT (Supports GET, PUT, PATCH)
# ==============================================================================
class WorkspaceDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def _get_tenant(self, request, tenant_id=None):
        if tenant_id:
            if str(request.user.tenant_id) != str(tenant_id):
                return None
            return Tenant.objects.filter(
                id=tenant_id,
                is_active=True,
                is_deleted=False,
            ).first()
        return request.user.tenant

    def get(self, request, tenant_id=None):
        tenant = self._get_tenant(request, tenant_id)
        if not tenant:
            return Response(
                {"error": "No active workspace found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(TenantSerializer(tenant).data)

    def put(self, request, tenant_id=None):
        return self._update(request, tenant_id, partial=True)

    def patch(self, request, tenant_id=None):
        return self._update(request, tenant_id, partial=True)

    def _update(self, request, tenant_id, partial):
        tenant = self._get_tenant(request, tenant_id)
        if not tenant:
            return Response(
                {"error": "No active workspace found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.user.role not in [User.RoleChoices.OWNER, User.RoleChoices.ADMIN]:
            return Response(
                {"error": "Only workspace owners or admins can modify agency settings."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = TenantSerializer(tenant, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save(updated_at_local=timezone.now())
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RotateInviteCodeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        tenant = request.user.tenant
        if not tenant:
            return Response(
                {"error": "No workspace found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.user.role not in [User.RoleChoices.OWNER, User.RoleChoices.ADMIN]:
            return Response(
                {"error": "Only workspace admins can rotate invite codes."},
                status=status.HTTP_403_FORBIDDEN,
            )

        tenant.invite_code = generate_invite_code()
        tenant.save(update_fields=['invite_code', 'updated_at_server'])
        return Response({"invite_code": tenant.invite_code}, status=status.HTTP_200_OK)


class ValidateInviteCodeView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        code = (
            request.query_params.get('invite_code')
            or request.query_params.get('code')
            or ''
        ).strip().upper()

        if not code:
            return Response(
                {"error": "Invite code parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        tenant = Tenant.objects.filter(
            invite_code=code,
            is_active=True,
            is_deleted=False,
        ).first()

        if not tenant:
            return Response(
                {"error": "Invalid or expired invite code."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response({
            "id": str(tenant.id),
            "name": tenant.name,
            "logo_url": tenant.logo_url,
            "official_phone": tenant.official_phone,
        }, status=status.HTTP_200_OK)


# ==============================================================================
# 3. USER PROFILE & TEAM (Supports GET, PUT, PATCH)
# ==============================================================================
class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def _get_target_user(self, request, user_id=None):
        if not user_id or str(request.user.id) == str(user_id):
            return request.user

        if request.user.role in [User.RoleChoices.OWNER, User.RoleChoices.ADMIN]:
            return User.objects.filter(
                id=user_id,
                tenant=request.user.tenant,
                is_active=True,
                is_deleted=False,
            ).first()

        return None

    def get(self, request, user_id=None):
        target_user = self._get_target_user(request, user_id)
        if not target_user:
            return Response(
                {"error": "User not found or access denied."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(UserProfileSerializer(target_user).data)

    def put(self, request, user_id=None):
        return self._update(request, user_id, partial=True)

    def patch(self, request, user_id=None):
        return self._update(request, user_id, partial=True)

    def _update(self, request, user_id, partial):
        target_user = self._get_target_user(request, user_id)
        if not target_user:
            return Response(
                {"error": "User not found or access denied."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = UserProfileSerializer(target_user, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save(updated_at_local=timezone.now())
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TeamMembersView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not request.user.tenant:
            return Response([])

        members = User.objects.filter(
            tenant=request.user.tenant,
            is_active=True,
            is_deleted=False,
        ).order_by('full_name')

        return Response(TeamMemberSerializer(members, many=True).data)


# ==============================================================================
# 4. FILE UPLOADS
# ==============================================================================

# In UploadTenantLogoView:
class UploadTenantLogoView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, tenant_id=None):
        tenant = request.user.tenant
        if not tenant:
            return Response({"error": "No workspace found."}, status=status.HTTP_404_NOT_FOUND)

        if request.user.role not in [User.RoleChoices.OWNER, User.RoleChoices.ADMIN]:
            return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        file_obj = request.FILES.get('logo')
        if not file_obj:
            return Response({"error": "No logo file provided."}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Save file to disk in media/logos/
        file_path = f"logos/{tenant.id}_{file_obj.name}"
        saved_path = default_storage.save(file_path, ContentFile(file_obj.read()))
        logo_url = request.build_absolute_uri(settings.MEDIA_URL + saved_path)

        # 2. Persist in database
        tenant.logo_url = logo_url
        tenant.save(update_fields=['logo_url', 'updated_at_server'])

        return Response({"logo_url": logo_url}, status=status.HTTP_200_OK)


# In UploadAvatarView:
class UploadAvatarView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, user_id=None):
        target_user = request.user
        file_obj = request.FILES.get('avatar')
        if not file_obj:
            return Response({"error": "No avatar file provided."}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Save file to disk in media/avatars/
        file_path = f"avatars/{target_user.id}_{file_obj.name}"
        saved_path = default_storage.save(file_path, ContentFile(file_obj.read()))
        avatar_url = request.build_absolute_uri(settings.MEDIA_URL + saved_path)

        # 2. Persist in database
        target_user.avatar_url = avatar_url
        target_user.save(update_fields=['avatar_url', 'updated_at_server'])

        return Response({"avatar_url": avatar_url}, status=status.HTTP_200_OK)