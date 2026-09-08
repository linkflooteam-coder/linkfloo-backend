from rest_framework import serializers
from .models import Tenant, User


# ==============================================================================
# 1. TENANT / WORKSPACE SERIALIZER
# ==============================================================================
class TenantSerializer(serializers.ModelSerializer):
    owner_id = serializers.UUIDField(source='owner.id', read_only=True)
    owner_name = serializers.CharField(source='owner.full_name', read_only=True, default='')

    website = serializers.CharField(
        required=False, 
        allow_blank=True, 
        allow_null=True
    )

    class Meta:
        model = Tenant
        fields = [
            'id',
            'name',
            'owner_id',
            'owner_name',
            'logo_url',
            'official_phone',
            'official_email',
            'website',
            'address',
            'rera_number',
            'gst_number',
            'primary_color_hex',
            'secondary_color_hex',
            'pdf_template_id',
            'show_company_logo_on_pdf',
            'show_company_phone_on_pdf',
            'show_company_email_on_pdf',
            'show_company_address_on_pdf',
            'show_company_website_on_pdf',
            'show_agent_name_on_pdf',
            'show_agent_phone_on_pdf',
            'show_agent_rera_on_pdf',
            'show_company_rera_on_pdf',
            'show_qr_code_on_pdf',
            'footer_disclaimer_text',
            'invite_code',
            'created_at_local',
            'updated_at_local',
            'is_active',
            'is_deleted',
        ]
        read_only_fields = [
            'id',
            'invite_code',
            'owner_id',
            'owner_name',
            'created_at_server',
            'updated_at_server',
        ]
        extra_kwargs = {
            'name': {'required': False, 'allow_blank': True},
            'logo_url': {'required': False, 'allow_null': True, 'allow_blank': True},
            'official_phone': {'required': False, 'allow_null': True, 'allow_blank': True},
            'official_email': {'required': False, 'allow_null': True, 'allow_blank': True},
            'website': {'required': False, 'allow_null': True, 'allow_blank': True},
            'address': {'required': False, 'allow_null': True, 'allow_blank': True},
            'rera_number': {'required': False, 'allow_null': True, 'allow_blank': True},
            'gst_number': {'required': False, 'allow_null': True, 'allow_blank': True},
            'primary_color_hex': {'required': False, 'allow_blank': True},
            'secondary_color_hex': {'required': False, 'allow_null': True, 'allow_blank': True},
            'pdf_template_id': {'required': False, 'allow_blank': True},
            'footer_disclaimer_text': {'required': False, 'allow_null': True, 'allow_blank': True},
            'created_at_local': {'required': False},
            'updated_at_local': {'required': False},
        }


# ==============================================================================
# 2. USER PROFILE SERIALIZER
# ==============================================================================
class UserProfileSerializer(serializers.ModelSerializer):
    tenant_id = serializers.UUIDField(source='tenant.id', read_only=True, allow_null=True)
    tenant_name = serializers.CharField(source='tenant.name', read_only=True, allow_null=True)
    invited_by_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'phone_number',
            'full_name',
            'email_address',
            'avatar_url',
            'designation',
            'personal_rera_number',
            'whatsapp_number',
            'fcm_token',
            'tenant_id',
            'tenant_name',
            'role',
            'invited_by_name',
            'is_active',
            'is_deleted',
            'last_login_at',
            'created_at_local',
            'updated_at_local',
        ]
        read_only_fields = [
            'id',
            'phone_number',
            'tenant_id',
            'tenant_name',
            'role',
            'invited_by_name',
            'created_at_server',
            'updated_at_server',
        ]
        extra_kwargs = {
            'full_name': {'required': False, 'allow_null': True, 'allow_blank': True},
            'email_address': {'required': False, 'allow_null': True, 'allow_blank': True},
            'avatar_url': {'required': False, 'allow_null': True, 'allow_blank': True},
            'designation': {'required': False, 'allow_null': True, 'allow_blank': True},
            'personal_rera_number': {'required': False, 'allow_null': True, 'allow_blank': True},
            'whatsapp_number': {'required': False, 'allow_null': True, 'allow_blank': True},
            'fcm_token': {'required': False, 'allow_null': True, 'allow_blank': True},
            'created_at_local': {'required': False},
            'updated_at_local': {'required': False},
        }

    def get_invited_by_name(self, obj):
        return obj.invited_by.full_name if obj.invited_by else ""


# ==============================================================================
# 3. TEAM MEMBER SERIALIZER
# ==============================================================================
class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'full_name',
            'phone_number',
            'whatsapp_number',
            'avatar_url',
            'designation',
            'personal_rera_number',
            'role',
            'is_active',
            'last_login_at',
        ]
        read_only_fields = fields