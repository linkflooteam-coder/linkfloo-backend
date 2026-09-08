from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Tenant, User


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'invite_code',
        'owner',
        'official_phone',
        'rera_number',
        'is_active',
        'is_deleted',
        'created_at_server',
    ]
    list_filter = ['is_active', 'is_deleted', 'created_at_server']
    search_fields = ['name', 'invite_code', 'official_phone', 'official_email', 'rera_number', 'gst_number']
    readonly_fields = ['id', 'invite_code', 'created_at_server', 'updated_at_server']
    
    fieldsets = (
        ('Agency Identity', {
            'fields': ('id', 'name', 'owner', 'invite_code', 'logo_url', 'is_active', 'is_deleted')
        }),
        ('Official Contact & Legal', {
            'fields': ('official_phone', 'official_email', 'website', 'address', 'rera_number', 'gst_number')
        }),
        ('Branding & PDF Theme', {
            'fields': ('primary_color_hex', 'secondary_color_hex', 'pdf_template_id')
        }),
        ('PDF Brochure Display Switches', {
            'classes': ('collapse',),
            'fields': (
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
            )
        }),
        ('Sync Timestamps', {
            'classes': ('collapse',),
            'fields': ('created_at_local', 'created_at_server', 'updated_at_local', 'updated_at_server')
        }),
    )


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        'phone_number',
        'full_name',
        'role',
        'tenant',
        'designation',
        'is_active',
        'is_staff',
        'last_login_at',
    ]
    list_filter = ['role', 'tenant', 'is_active', 'is_staff', 'is_deleted']
    search_fields = ['phone_number', 'full_name', 'email_address', 'personal_rera_number']
    ordering = ['phone_number']
    readonly_fields = ['id', 'last_login_at', 'created_at_server', 'updated_at_server']

    # Custom fieldsets since we use phone_number instead of username
    fieldsets = (
        ('Authentication', {
            'fields': ('id', 'phone_number', 'password')
        }),
        ('Personal Profile', {
            'fields': ('full_name', 'email_address', 'avatar_url', 'whatsapp_number')
        }),
        ('Workspace & Credentials', {
            'fields': ('tenant', 'role', 'designation', 'personal_rera_number', 'invited_by')
        }),
        ('Push Notifications & System', {
            'classes': ('collapse',),
            'fields': ('fcm_token', 'last_login_at')
        }),
        ('Permissions & Status', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_deleted', 'groups', 'user_permissions')
        }),
        ('Sync Timestamps', {
            'classes': ('collapse',),
            'fields': ('created_at_local', 'created_at_server', 'updated_at_local', 'updated_at_server')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'full_name', 'role', 'tenant', 'is_staff', 'is_superuser'),
        }),
    )