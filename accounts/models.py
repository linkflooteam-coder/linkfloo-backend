import uuid
import random
import string
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.conf import settings


def generate_invite_code():
    """Generates a clean 6-character alphanumeric agency code (excluding ambiguous chars 0, O, 1, I)."""
    chars = ''.join([c for c in string.ascii_uppercase + string.digits if c not in '0O1I'])
    return ''.join(random.choices(chars, k=6))


# ==============================================================================
# 0. ABSTRACT BASE SYNC MODEL
# ==============================================================================
class BaseSyncModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at_local = models.DateTimeField(default=timezone.now)
    created_at_server = models.DateTimeField(auto_now_add=True)
    updated_at_local = models.DateTimeField(default=timezone.now)
    updated_at_server = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


# ==============================================================================
# 1. TENANT / AGENCY WORKSPACE MODEL
# ==============================================================================
class Tenant(BaseSyncModel):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_workspaces'
    )
    logo_url = models.URLField(max_length=1000, null=True, blank=True)

    # Official Agency Contact Details
    official_phone = models.CharField(max_length=20, null=True, blank=True)
    official_email = models.EmailField(max_length=255, null=True, blank=True)
    website = models.URLField(max_length=500, null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    # Compliance (Indian Real Estate / RERA / GST)
    rera_number = models.CharField(max_length=100, null=True, blank=True)
    gst_number = models.CharField(max_length=50, null=True, blank=True)

    # Visual Branding & PDF Styling
    primary_color_hex = models.CharField(max_length=10, default='#1E3A8A')
    secondary_color_hex = models.CharField(max_length=10, null=True, blank=True)
    pdf_template_id = models.CharField(max_length=50, default='modern_minimal')

    # Granular PDF Brochure Switches
    show_company_logo_on_pdf = models.BooleanField(default=True)
    show_company_phone_on_pdf = models.BooleanField(default=True)
    show_company_email_on_pdf = models.BooleanField(default=True)
    show_company_address_on_pdf = models.BooleanField(default=True)
    show_company_website_on_pdf = models.BooleanField(default=True)

    show_agent_name_on_pdf = models.BooleanField(default=True)
    show_agent_phone_on_pdf = models.BooleanField(default=True)
    show_agent_rera_on_pdf = models.BooleanField(default=True)

    show_company_rera_on_pdf = models.BooleanField(default=True)
    show_qr_code_on_pdf = models.BooleanField(default=True)
    footer_disclaimer_text = models.TextField(null=True, blank=True)

    # Team Onboarding
    invite_code = models.CharField(max_length=12, unique=True, default=generate_invite_code, db_index=True)

    class Meta:
        db_table = 'tenants'
        ordering = ['-created_at_server']
        indexes = [
            models.Index(fields=['invite_code']),
            models.Index(fields=['updated_at_server']),
        ]

    def __str__(self):
        return self.name or f"Workspace ({self.id})"


# ==============================================================================
# 2. CUSTOM USER MANAGER
# ==============================================================================
class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('Phone number is required.')
        user = self.model(phone_number=phone_number, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone_number, password, **extra_fields)


# ==============================================================================
# 3. CUSTOM USER MODEL
# ==============================================================================
class User(AbstractBaseUser, PermissionsMixin, BaseSyncModel):
    class RoleChoices(models.TextChoices):
        OWNER = 'owner', 'Workspace Owner'
        ADMIN = 'admin', 'Agency Admin'
        AGENT = 'agent', 'Sales Consultant'
        CHANNEL_PARTNER = 'partner', 'Channel Partner'

    phone_number = models.CharField(max_length=20, unique=True, db_index=True)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    email_address = models.EmailField(max_length=255, null=True, blank=True)
    avatar_url = models.URLField(max_length=1000, null=True, blank=True)

    # Credentials & Contact
    designation = models.CharField(max_length=100, null=True, blank=True, default='Sales Consultant')
    personal_rera_number = models.CharField(max_length=100, null=True, blank=True)
    whatsapp_number = models.CharField(max_length=20, null=True, blank=True)
    fcm_token = models.TextField(null=True, blank=True)
    last_login_at = models.DateTimeField(null=True, blank=True)

    # Workspace & Hierarchy
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members'
    )
    role = models.CharField(max_length=30, choices=RoleChoices.choices, default=RoleChoices.AGENT)
    invited_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invited_members'
    )

    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    class Meta:
        db_table = 'users'
        ordering = ['full_name', 'phone_number']
        indexes = [
            models.Index(fields=['tenant', 'role']),
            models.Index(fields=['tenant', 'updated_at_server']),
        ]

    def __str__(self):
        tenant_label = self.tenant.name if self.tenant else 'Independent'
        return f"{self.full_name or self.phone_number} ({self.role}) - {tenant_label}"