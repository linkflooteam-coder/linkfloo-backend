# from django.contrib import admin
# from django.utils import timezone
# from .models import Lead, Property, PropertyMedia, Message, ActivityLog, UserDevice

# class PropertyMediaInline(admin.TabularInline):
#     model = PropertyMedia
#     extra = 1
#     fields = ['media_type', 'is_cover', 'sort_order', 'remote_url', 'upload_status', 'is_deleted']
#     readonly_fields = ['created_at_server', 'updated_at_server']


# @admin.register(Lead)
# class LeadAdmin(admin.ModelAdmin):
#     list_display = [
#         'full_name',
#         'phone_number',
#         'workflow_status',
#         'budget_range_display',
#         'locality_wanted',
#         'tenant',
#         'next_follow_up_at',
#         'is_deleted',
#     ]
#     list_filter = ['workflow_status', 'transaction_type', 'tenant', 'is_deleted', 'lead_source']
#     search_fields = ['full_name', 'phone_number', 'email_address', 'locality_wanted', 'requirements_notes']
#     readonly_fields = ['id', 'created_at_server', 'updated_at_server']

#     fieldsets = (
#         ('Lead Identity', {
#             'fields': ('id', 'tenant', 'full_name', 'phone_number', 'email_address', 'avatar_url', 'is_deleted')
#         }),
#         ('Requirements & Budget', {
#             'fields': (
#                 'requirements_notes',
#                 ('budget_min', 'budget_max'),
#                 'transaction_type',
#                 'property_category_wanted',
#                 'property_sub_type_wanted',
#                 'property_sub_type_other_label',
#                 'bhk_wanted',
#                 'locality_wanted',
#                 'usage_purpose',
#                 'timeline',
#                 'lead_source',
#             )
#         }),
#         ('Pipeline Stage & Assignment', {
#             'fields': (
#                 'workflow_status',
#                 'next_follow_up_at',
#                 'assigned_agent_id',
#                 'linked_property_id',
#             )
#         }),
#         ('Chat Preview Cache', {
#             'classes': ('collapse',),
#             'fields': ('last_message_preview', 'last_message_at', 'unread_messages_count')
#         }),
#         ('Sync Timestamps', {
#             'classes': ('collapse',),
#             'fields': ('created_at_local', 'created_at_server', 'updated_at_local', 'updated_at_server')
#         }),
#     )

#     def delete_model(self, request, obj):
#         obj.is_deleted = True
#         obj.updated_at_server = timezone.now()
#         obj.save(update_fields=['is_deleted', 'updated_at_server'])

#     def delete_queryset(self, request, queryset):
#         queryset.update(is_deleted=True, updated_at_server=timezone.now())

#     @admin.display(description='Budget (INR)')
#     def budget_range_display(self, obj):
#         if obj.budget_min and obj.budget_max:
#             return f"₹{obj.budget_min:,.0f} - ₹{obj.budget_max:,.0f}"
#         if obj.budget_max:
#             return f"Up to ₹{obj.budget_max:,.0f}"
#         if obj.budget_min:
#             return f"From ₹{obj.budget_min:,.0f}"
#         return "-"


# @admin.register(Property)
# class PropertyAdmin(admin.ModelAdmin):
#     list_display = [
#         'title',
#         'price_min',
#         'category',
#         'transaction_type',
#         'bhk',
#         'locality',
#         'city',
#         'listing_status',
#         'visibility',
#         'tenant',
#         'is_deleted',
#     ]
#     list_filter = ['listing_status', 'visibility', 'category', 'transaction_type', 'tenant', 'city', 'is_deleted']
#     search_fields = ['title', 'locality', 'city', 'pincode', 'rera_number', 'owner_contact_name', 'owner_contact_phone']
#     readonly_fields = ['id', 'created_at_server', 'updated_at_server']
#     inlines = [PropertyMediaInline]

#     fieldsets = (
#         ('Property Classification', {
#             'fields': (
#                 'id', 'tenant', 'title', 'category', 'sub_type',
#                 'sub_type_other_label', 'transaction_type', 'bhk', 'assigned_agent_id', 'is_deleted'
#             )
#         }),
#         ('Measurements & Structure', {
#             'fields': (
#                 ('area_value', 'area_unit'),
#                 'furnishing_status',
#                 ('floor_number', 'total_floors'),
#             )
#         }),
#         ('Pricing & Rent Details', {
#             'fields': (
#                 ('price_min', 'price_max', 'is_price_negotiable'),
#                 'security_deposit_amount',
#                 'maintenance_charge_monthly',
#             )
#         }),
#         ('RERA & Possession Timeline', {
#             'fields': ('rera_number', 'possession_status', 'possession_date')
#         }),
#         ('Location & Address', {
#             'fields': (
#                 'pincode', 'locality', 'city', 'state', 'landmark',
#                 ('latitude', 'longitude')
#             )
#         }),
#         ('Owner Records (Internal Only)', {
#             'classes': ('collapse',),
#             'fields': ('owner_contact_name', 'owner_contact_phone')
#         }),
#         ('Visibility & Discovery', {
#             'fields': ('listing_status', 'visibility', 'allow_platform_contact', 'description', 'amenities_notes')
#         }),
#         ('Sync Timestamps', {
#             'classes': ('collapse',),
#             'fields': ('created_at_local', 'created_at_server', 'updated_at_local', 'updated_at_server')
#         }),
#     )

#     def delete_model(self, request, obj):
#         obj.is_deleted = True
#         obj.updated_at_server = timezone.now()
#         obj.save(update_fields=['is_deleted', 'updated_at_server'])

#     def delete_queryset(self, request, queryset):
#         queryset.update(is_deleted=True, updated_at_server=timezone.now())

#     # Handles soft-deletion for photos removed via the inline table
#     def save_formset(self, request, form, formset, change):
#         instances = formset.save(commit=False)
#         for obj in formset.deleted_objects:
#             obj.is_deleted = True
#             obj.updated_at_server = timezone.now()
#             obj.save(update_fields=['is_deleted', 'updated_at_server'])
#         for instance in instances:
#             instance.save()
#         formset.save_m2m()


# @admin.register(PropertyMedia)
# class PropertyMediaAdmin(admin.ModelAdmin):
#     list_display = ['property', 'media_type', 'is_cover', 'sort_order', 'upload_status', 'tenant', 'is_deleted']
#     list_filter = ['media_type', 'upload_status', 'is_cover', 'tenant', 'is_deleted']
#     search_fields = ['property__title', 'remote_url', 'file_path']
#     readonly_fields = ['id', 'created_at_server', 'updated_at_server']

#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         # If filtering explicitly by is_deleted in the right sidebar, show it; otherwise hide deleted
#         if 'is_deleted__exact' in request.GET:
#             return qs
#         return qs.filter(is_deleted=False)

#     def delete_model(self, request, obj):
#         obj.is_deleted = True
#         obj.updated_at_server = timezone.now()
#         obj.save(update_fields=['is_deleted', 'updated_at_server'])

#     def delete_queryset(self, request, queryset):
#         queryset.update(is_deleted=True, updated_at_server=timezone.now())


# @admin.register(Message)
# class MessageAdmin(admin.ModelAdmin):
#     list_display = [
#         'lead',
#         'created_by_user_id',
#         'kind',
#         'prompt_type',
#         'delivery_status',
#         'is_read',
#         'sent_at',
#         'tenant',
#         'is_deleted',
#     ]
#     list_filter = ['kind', 'prompt_type', 'delivery_status', 'is_read', 'tenant', 'is_deleted']
#     search_fields = ['content', 'selected_value', 'lead__full_name', 'lead__phone_number']
#     readonly_fields = ['id', 'sent_at', 'created_at_server', 'updated_at_server']

#     fieldsets = (
#         ('Message Context', {
#             'fields': ('id', 'tenant', 'lead', 'created_by_user_id', 'property_id', 'reply_to_message_id', 'is_deleted')
#         }),
#         ('Message Content & Interactive State', {
#             'fields': ('kind', 'prompt_type', 'content', 'selected_value', 'is_action_completed')
#         }),
#         ('Attachments & Media', {
#             'fields': ('attachment_local_path', 'attachment_remote_url', 'attachment_upload_status')
#         }),
#         ('Delivery & Time Release', {
#             'fields': ('delivery_status', 'is_read', 'sent_at', 'show_after')
#         }),
#         ('Sync Timestamps', {
#             'classes': ('collapse',),
#             'fields': ('created_at_local', 'created_at_server', 'updated_at_local', 'updated_at_server')
#         }),
#     )


# @admin.register(ActivityLog)
# class ActivityLogAdmin(admin.ModelAdmin):
#     list_display = [
#         'type',
#         'lead_name',
#         'lead_phone',
#         'agent_id',
#         'occurred_at',
#         'seen_at',
#         'tenant',
#     ]
#     list_filter = ['type', 'tenant', 'occurred_at']
#     search_fields = ['lead_name', 'lead_phone', 'selected_value']
#     readonly_fields = [
#         'id', 'tenant', 'agent_id', 'lead_id', 'message_id', 'type',
#         'occurred_at', 'count', 'lead_name', 'lead_phone', 'selected_value',
#         'follow_up_date', 'seen_at', 'created_at_local', 'created_at_server',
#         'updated_at_local', 'updated_at_server',
#     ]

#     def has_add_permission(self, request):
#         return False

#     def has_delete_permission(self, request, obj=None):
#         return False

# @admin.register(UserDevice)
# class UserDeviceAdmin(admin.ItemAdmin if hasattr(admin, 'ItemAdmin') else admin.ModelAdmin):
#     list_display = ('user', 'platform', 'fcm_token', 'updated_at')
#     search_fields = ('user__username', 'user__email', 'fcm_token')
#     list_filter = ('platform', 'updated_at')

from django.contrib import admin
from django.utils import timezone
from .models import (
    Project,
    Property,
    PropertyMedia,
    Lead,
    Message,
    ActivityLog,
    UserDevice,
)


# ==============================================================================
# INLINES
# ==============================================================================

class PropertyMediaInline(admin.TabularInline):
    model = PropertyMedia
    extra = 1
    fields = [
        'media_type',
        'is_cover',
        'sort_order',
        'remote_url',
        'file_path',
        'upload_status',
        'is_deleted',
    ]
    readonly_fields = ['created_at_server', 'updated_at_server']


class PropertyUnitInline(admin.TabularInline):
    """Shows units belonging to a master Project/Society directly inside the project view."""
    model = Property
    extra = 0
    fields = [
        'unit_number',
        'tower_block_name',
        'title',
        'transaction_type',
        'bhk_count',
        'carpet_area',
        'price_min',
        'listing_status',
    ]
    readonly_fields = [
        'unit_number',
        'tower_block_name',
        'title',
        'transaction_type',
        'bhk_count',
        'carpet_area',
        'price_min',
        'listing_status',
    ]
    show_change_link = True
    can_delete = False


# ==============================================================================
# 1. MASTER PROJECT ADMIN
# ==============================================================================

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = [
        'project_name',
        'developer_name',
        'city',
        'locality',
        'total_units',
        'total_towers',
        'tenant',
        'is_deleted',
    ]
    list_filter = ['tenant', 'city', 'is_deleted']
    search_fields = ['project_name', 'developer_name', 'city', 'locality', 'master_rera_number']
    readonly_fields = ['id', 'created_at_server', 'updated_at_server']
    inlines = [PropertyUnitInline]

    fieldsets = (
        ('Project Identity', {
            'fields': (
                'id',
                'tenant',
                'assigned_agent_id',
                'project_name',
                'developer_name',
                'master_rera_number',
                'is_deleted',
            )
        }),
        ('Scale & Handover Schedule', {
            'fields': (
                'total_land_area_acres',
                ('total_towers', 'total_units'),
                ('launch_date', 'expected_handover_date'),
            )
        }),
        ('Location & Address', {
            'fields': (
                'address_line',
                ('locality', 'landmark'),
                ('city', 'state', 'pincode'),
                ('latitude', 'longitude'),
            )
        }),
        ('Amenities & Collateral', {
            'fields': (
                'standard_amenity_ids',
                'custom_amenities',
                'master_brochure_url',
                'master_layout_plan_url',
                'cover_image_url',
            )
        }),
        ('Sync Bookkeeping', {
            'classes': ('collapse',),
            'fields': ('created_at_local', 'created_at_server', 'updated_at_local', 'updated_at_server'),
        }),
    )

    def delete_model(self, request, obj):
        obj.is_deleted = True
        obj.updated_at_server = timezone.now()
        obj.save(update_fields=['is_deleted', 'updated_at_server'])

    def delete_queryset(self, request, queryset):
        queryset.update(is_deleted=True, updated_at_server=timezone.now())


# ==============================================================================
# 2. PROPERTY / INVENTORY ADMIN
# ==============================================================================

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'society_or_project_name',
        'unit_number',
        'price_display',
        'category',
        'transaction_type',
        'bhk_count',
        'carpet_area_display',
        'locality',
        'city',
        'listing_status',
        'tenant',
        'is_deleted',
    ]
    list_filter = [
        'listing_status',
        'visibility',
        'category',
        'transaction_type',
        'mandate_type',
        'is_co_broke_listing',
        'tenant',
        'city',
        'is_deleted',
    ]
    search_fields = [
        'title',
        'society_or_project_name',
        'tower_block_name',
        'unit_number',
        'locality',
        'city',
        'pincode',
        'rera_number',
        'owner_contact_name',
        'owner_contact_phone',
        'co_broker_name',
    ]
    readonly_fields = ['id', 'created_at_server', 'updated_at_server']
    inlines = [PropertyMediaInline]

    fieldsets = (
        ('Listing Identity & Classification', {
            'fields': (
                'id',
                'tenant',
                'assigned_agent_id',
                'title',
                'category',
                ('sub_type', 'sub_type_other_label'),
                ('transaction_type', 'mandate_type'),
                'is_deleted',
            )
        }),
        ('Project / Society Hierarchy', {
            'fields': (
                'project',
                'society_or_project_name',
                ('tower_block_name', 'unit_number'),
            )
        }),
        ('Configuration & Dimensions', {
            'fields': (
                ('bhk_count', 'bathrooms_count', 'balconies_count'),
                ('carpet_area', 'super_built_up_area', 'area_unit'),
                ('floor_number', 'total_floors'),
                ('facing', 'furnishing_status'),
                ('parking_count', 'parking_type'),
            )
        }),
        ('Commercial & Land Specifications', {
            'classes': ('collapse',),
            'fields': (
                'commercial_fitout',
                ('workstations_count', 'cabins_count', 'meeting_rooms_count'),
                ('road_width_feet', 'is_corner_plot'),
            )
        }),
        ('Commercial Terms & Financials', {
            'fields': (
                ('price_min', 'price_max'),
                ('is_price_negotiable', 'is_all_inclusive_price'),
                ('security_deposit_amount', 'maintenance_charge_monthly'),
                ('lock_in_period_months', 'expected_rental_yield'),
            )
        }),
        ('Amenities & Features', {
            'fields': (
                'standard_amenity_ids',
                'custom_amenities',
                'description',
            )
        }),
        ('Confidential Agency Vault', {
            'classes': ('collapse',),
            'fields': (
                'occupancy_status',
                ('owner_contact_name', 'owner_contact_phone'),
                ('key_arrangement', 'key_contact_details'),
                'internal_private_notes',
            )
        }),
        ('B2B Co-Broking Terms', {
            'classes': ('collapse',),
            'fields': (
                'is_co_broke_listing',
                ('co_broker_name', 'co_broker_phone'),
                'co_broker_agency',
                'commission_terms',
            )
        }),
        ('Compliance, Title & Possession', {
            'classes': ('collapse',),
            'fields': (
                'rera_number',
                'possession_status',
                'possession_date',
                'age_of_property_years',
                'ownership_type',
            )
        }),
        ('Location & Geo', {
            'fields': (
                'locality',
                'landmark',
                ('city', 'state', 'pincode'),
                ('latitude', 'longitude'),
            )
        }),
        ('Visibility & Discovery', {
            'fields': (
                'listing_status',
                'visibility',
                'allow_platform_contact',
            )
        }),
        ('Sync Bookkeeping', {
            'classes': ('collapse',),
            'fields': ('created_at_local', 'created_at_server', 'updated_at_local', 'updated_at_server'),
        }),
    )

    @admin.display(description='Price Target')
    def price_display(self, obj):
        if obj.price_min and obj.price_max and obj.price_min != obj.price_max:
            return f"₹{obj.price_min:,.0f} - ₹{obj.price_max:,.0f}"
        if obj.price_min:
            return f"₹{obj.price_min:,.0f}"
        if obj.price_max:
            return f"₹{obj.price_max:,.0f}"
        return "On Request"

    @admin.display(description='Carpet Area')
    def carpet_area_display(self, obj):
        if obj.carpet_area:
            return f"{obj.carpet_area:,.0f} {obj.get_area_unit_display()}"
        if obj.super_built_up_area:
            return f"{obj.super_built_up_area:,.0f} (Super)"
        return "-"

    def delete_model(self, request, obj):
        obj.is_deleted = True
        obj.updated_at_server = timezone.now()
        obj.save(update_fields=['is_deleted', 'updated_at_server'])

    def delete_queryset(self, request, queryset):
        queryset.update(is_deleted=True, updated_at_server=timezone.now())

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.is_deleted = True
            obj.updated_at_server = timezone.now()
            obj.save(update_fields=['is_deleted', 'updated_at_server'])
        for instance in instances:
            instance.save()
        formset.save_m2m()


# ==============================================================================
# 3. LEAD ADMIN
# ==============================================================================

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = [
        'full_name',
        'phone_number',
        'workflow_status',
        'budget_range_display',
        'locality_wanted',
        'tenant',
        'next_follow_up_at',
        'is_deleted',
    ]
    list_filter = ['workflow_status', 'transaction_type', 'tenant', 'is_deleted', 'lead_source']
    search_fields = ['full_name', 'phone_number', 'email_address', 'locality_wanted', 'requirements_notes']
    readonly_fields = ['id', 'created_at_server', 'updated_at_server']

    fieldsets = (
        ('Lead Identity', {
            'fields': ('id', 'tenant', 'full_name', 'phone_number', 'email_address', 'avatar_url', 'is_deleted')
        }),
        ('Requirements & Budget', {
            'fields': (
                'requirements_notes',
                ('budget_min', 'budget_max'),
                'transaction_type',
                'property_category_wanted',
                'property_sub_type_wanted',
                'property_sub_type_other_label',
                'bhk_wanted',
                'locality_wanted',
                'usage_purpose',
                'timeline',
                'lead_source',
            )
        }),
        ('Pipeline Stage & Assignment', {
            'fields': (
                'workflow_status',
                'next_follow_up_at',
                'assigned_agent_id',
                'linked_property_id',
            )
        }),
        ('Chat Preview Cache', {
            'classes': ('collapse',),
            'fields': ('last_message_preview', 'last_message_at', 'unread_messages_count')
        }),
        ('Sync Bookkeeping', {
            'classes': ('collapse',),
            'fields': ('created_at_local', 'created_at_server', 'updated_at_local', 'updated_at_server')
        }),
    )

    def delete_model(self, request, obj):
        obj.is_deleted = True
        obj.updated_at_server = timezone.now()
        obj.save(update_fields=['is_deleted', 'updated_at_server'])

    def delete_queryset(self, request, queryset):
        queryset.update(is_deleted=True, updated_at_server=timezone.now())

    @admin.display(description='Budget (INR)')
    def budget_range_display(self, obj):
        if obj.budget_min and obj.budget_max:
            return f"₹{obj.budget_min:,.0f} - ₹{obj.budget_max:,.0f}"
        if obj.budget_max:
            return f"Up to ₹{obj.budget_max:,.0f}"
        if obj.budget_min:
            return f"From ₹{obj.budget_min:,.0f}"
        return "-"


# ==============================================================================
# 4. MEDIA, MESSAGES, ACTIVITY & DEVICES
# ==============================================================================

@admin.register(PropertyMedia)
class PropertyMediaAdmin(admin.ModelAdmin):
    list_display = ['property', 'media_type', 'is_cover', 'sort_order', 'upload_status', 'tenant', 'is_deleted']
    list_filter = ['media_type', 'upload_status', 'is_cover', 'tenant', 'is_deleted']
    search_fields = ['property__title', 'remote_url', 'file_path']
    readonly_fields = ['id', 'created_at_server', 'updated_at_server']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if 'is_deleted__exact' in request.GET:
            return qs
        return qs.filter(is_deleted=False)

    def delete_model(self, request, obj):
        obj.is_deleted = True
        obj.updated_at_server = timezone.now()
        obj.save(update_fields=['is_deleted', 'updated_at_server'])

    def delete_queryset(self, request, queryset):
        queryset.update(is_deleted=True, updated_at_server=timezone.now())


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = [
        'lead',
        'created_by_user_id',
        'kind',
        'prompt_type',
        'delivery_status',
        'is_read',
        'sent_at',
        'tenant',
        'is_deleted',
    ]
    list_filter = ['kind', 'prompt_type', 'delivery_status', 'is_read', 'tenant', 'is_deleted']
    search_fields = ['content', 'selected_value', 'lead__full_name', 'lead__phone_number']
    readonly_fields = ['id', 'sent_at', 'created_at_server', 'updated_at_server']

    fieldsets = (
        ('Message Context', {
            'fields': ('id', 'tenant', 'lead', 'created_by_user_id', 'property_id', 'reply_to_message_id', 'is_deleted')
        }),
        ('Content & State', {
            'fields': ('kind', 'prompt_type', 'content', 'selected_value', 'is_action_completed')
        }),
        ('Media Attachments', {
            'fields': ('attachment_local_path', 'attachment_remote_url', 'attachment_upload_status')
        }),
        ('Delivery Pipeline', {
            'fields': ('delivery_status', 'is_read', 'sent_at', 'show_after')
        }),
        ('Sync Bookkeeping', {
            'classes': ('collapse',),
            'fields': ('created_at_local', 'created_at_server', 'updated_at_local', 'updated_at_server')
        }),
    )


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = [
        'type',
        'lead_name',
        'lead_phone',
        'agent_id',
        'occurred_at',
        'seen_at',
        'tenant',
    ]
    list_filter = ['type', 'tenant', 'occurred_at']
    search_fields = ['lead_name', 'lead_phone', 'selected_value']
    readonly_fields = [
        'id', 'tenant', 'agent_id', 'lead_id', 'message_id', 'type',
        'occurred_at', 'count', 'lead_name', 'lead_phone', 'selected_value',
        'follow_up_date', 'seen_at', 'created_at_local', 'created_at_server',
        'updated_at_local', 'updated_at_server',
    ]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(UserDevice)
class UserDeviceAdmin(admin.ModelAdmin):
    list_display = ('user', 'platform', 'fcm_token', 'updated_at')
    search_fields = ('user__username', 'user__email', 'fcm_token')
    list_filter = ('platform', 'updated_at')