# from rest_framework import serializers
# from .models import Lead, Property, PropertyMedia, Message, ActivityLog


# class LeadSyncSerializer(serializers.ModelSerializer):
#     tenant_id = serializers.UUIDField(source='tenant.id', read_only=True)

#     class Meta:
#         model = Lead
#         fields = [
#             'id', 'tenant_id', 'created_at_local', 'created_at_server',
#             'updated_at_local', 'updated_at_server', 'is_deleted',
#             'full_name', 'phone_number', 'email_address', 'avatar_url',
#             'requirements_notes', 'budget_min', 'budget_max',
#             'transaction_type', 'property_category_wanted', 'property_sub_type_wanted',
#             'property_sub_type_other_label', 'bhk_wanted', 'locality_wanted',
#             'lead_source', 'usage_purpose', 'timeline', 'workflow_status',
#             'next_follow_up_at', 'assigned_agent_id', 'linked_property_id',
#             'last_message_preview', 'last_message_at', 'unread_messages_count'
#         ]
#         read_only_fields = ['created_at_server', 'updated_at_server']


# class PropertySyncSerializer(serializers.ModelSerializer):
#     tenant_id = serializers.UUIDField(source='tenant.id', read_only=True)

#     class Meta:
#         model = Property
#         fields = [
#             'id', 'tenant_id', 'assigned_agent_id',
#             'created_at_local', 'created_at_server', 'updated_at_local', 'updated_at_server',
#             'is_deleted', 'title', 'category', 'sub_type', 'sub_type_other_label',
#             'transaction_type', 'bhk', 'area_value', 'area_unit', 'furnishing_status',
#             'floor_number', 'total_floors', 'price_min', 'price_max',
#             'is_price_negotiable', 'security_deposit_amount', 'maintenance_charge_monthly',
#             'rera_number', 'possession_status', 'possession_date', 'pincode',
#             'city', 'state', 'locality', 'landmark', 'latitude', 'longitude',
#             'owner_contact_name', 'owner_contact_phone', 'listing_status',
#             'visibility', 'allow_platform_contact', 'description', 'amenities_notes'
#         ]
#         read_only_fields = ['created_at_server', 'updated_at_server']


# class PropertyMediaSyncSerializer(serializers.ModelSerializer):
#     tenant_id = serializers.UUIDField(source='tenant.id', read_only=True)
#     property_id = serializers.UUIDField(source='property.id')

#     class Meta:
#         model = PropertyMedia
#         fields = [
#             'id', 'tenant_id', 'property_id',
#             'created_at_local', 'created_at_server', 'updated_at_local', 'updated_at_server',
#             'is_deleted', 'media_type', 'sort_order', 'is_cover', 'file_path',
#             'remote_url', 'thumbnail_path', 'upload_status', 'upload_retry_count',
#             'file_size_bytes'
#         ]
#         read_only_fields = ['created_at_server', 'updated_at_server']


# class MessageSyncSerializer(serializers.ModelSerializer):
#     tenant_id = serializers.UUIDField(source='tenant.id', read_only=True)
#     lead_id = serializers.UUIDField(source='lead.id')

#     class Meta:
#         model = Message
#         fields = [
#             'id', 'tenant_id', 'lead_id', 'created_by_user_id', 'property_id',
#             'reply_to_message_id', 'kind', 'prompt_type', 'content', 'selected_value',
#             'is_action_completed', 'attachment_local_path', 'attachment_remote_url',
#             'attachment_upload_status', 'delivery_status', 'is_read', 'sent_at',
#             'show_after', 'created_at_local', 'created_at_server', 'updated_at_local',
#             'updated_at_server', 'is_deleted'
#         ]
#         read_only_fields = ['created_at_server', 'updated_at_server']


# class ActivityLogSyncSerializer(serializers.ModelSerializer):
#     tenant_id = serializers.UUIDField(source='tenant.id', read_only=True)

#     class Meta:
#         model = ActivityLog
#         fields = [
#             'id', 'tenant_id', 'agent_id', 'lead_id', 'message_id', 'type',
#             'occurred_at', 'count', 'lead_name', 'lead_phone', 'selected_value',
#             'follow_up_date', 'seen_at', 'created_at_local', 'created_at_server',
#             'updated_at_local', 'updated_at_server'
#         ]
#         read_only_fields = ['created_at_server', 'updated_at_server']

from rest_framework import serializers
from .models import (
    Lead,
    Project,
    Property,
    PropertyMedia,
    Message,
    ActivityLog,
)


# ==============================================================================
# 1. PROJECT SYNC SERIALIZER
# ==============================================================================
class ProjectSyncSerializer(serializers.ModelSerializer):
    tenant_id = serializers.UUIDField(source='tenant.id', read_only=True)

    class Meta:
        model = Project
        fields = [
            'id',
            'tenant_id',
            'assigned_agent_id',
            'created_at_local',
            'created_at_server',
            'updated_at_local',
            'updated_at_server',
            'is_deleted',
            'project_name',
            'developer_name',
            'master_rera_number',
            'total_land_area_acres',
            'total_towers',
            'total_units',
            'launch_date',
            'expected_handover_date',
            'pincode',
            'city',
            'state',
            'locality',
            'address_line',
            'landmark',
            'latitude',
            'longitude',
            'standard_amenity_ids',
            'custom_amenities',
            'master_brochure_url',
            'master_layout_plan_url',
            'cover_image_url',
        ]
        read_only_fields = ['created_at_server', 'updated_at_server']


# ==============================================================================
# 2. PROPERTY SYNC SERIALIZER
# ==============================================================================
class PropertySyncSerializer(serializers.ModelSerializer):
    tenant_id = serializers.UUIDField(source='tenant.id', read_only=True)
    project_id = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(),
        source='project',
        allow_null=True,
        required=False,
    )

    class Meta:
        model = Property
        fields = [
            'id',
            'tenant_id',
            'assigned_agent_id',
            'project_id',
            'society_or_project_name',
            'tower_block_name',
            'unit_number',
            'created_at_local',
            'created_at_server',
            'updated_at_local',
            'updated_at_server',
            'is_deleted',
            'title',
            'category',
            'sub_type',
            'sub_type_other_label',
            'transaction_type',
            'mandate_type',
            'bhk_count',
            'bathrooms_count',
            'balconies_count',
            'facing',
            'carpet_area',
            'super_built_up_area',
            'area_unit',
            'floor_number',
            'total_floors',
            'furnishing_status',
            'parking_count',
            'parking_type',
            'commercial_fitout',
            'workstations_count',
            'cabins_count',
            'meeting_rooms_count',
            'road_width_feet',
            'is_corner_plot',
            'price_min',
            'price_max',
            'is_price_negotiable',
            'is_all_inclusive_price',
            'security_deposit_amount',
            'maintenance_charge_monthly',
            'lock_in_period_months',
            'expected_rental_yield',
            'standard_amenity_ids',
            'custom_amenities',
            'occupancy_status',
            'owner_contact_name',
            'owner_contact_phone',
            'key_arrangement',
            'key_contact_details',
            'is_co_broke_listing',
            'co_broker_name',
            'co_broker_phone',
            'co_broker_agency',
            'commission_terms',
            'rera_number',
            'possession_status',
            'possession_date',
            'age_of_property_years',
            'ownership_type',
            'pincode',
            'city',
            'state',
            'locality',
            'landmark',
            'latitude',
            'longitude',
            'description',
            'internal_private_notes',
            'listing_status',
            'visibility',
            'allow_platform_contact',
        ]
        read_only_fields = ['created_at_server', 'updated_at_server']


# ==============================================================================
# 3. LEAD SYNC SERIALIZER
# ==============================================================================
class LeadSyncSerializer(serializers.ModelSerializer):
    tenant_id = serializers.UUIDField(source='tenant.id', read_only=True)

    class Meta:
        model = Lead
        fields = [
            'id',
            'tenant_id',
            'created_at_local',
            'created_at_server',
            'updated_at_local',
            'updated_at_server',
            'is_deleted',
            'full_name',
            'phone_number',
            'email_address',
            'avatar_url',
            'requirements_notes',
            'budget_min',
            'budget_max',
            'transaction_type',
            'property_category_wanted',
            'property_sub_type_wanted',
            'property_sub_type_other_label',
            'bhk_wanted',
            'locality_wanted',
            'lead_source',
            'usage_purpose',
            'timeline',
            'workflow_status',
            'next_follow_up_at',
            'assigned_agent_id',
            'linked_property_id',
            'last_message_preview',
            'last_message_at',
            'unread_messages_count',
        ]
        read_only_fields = ['created_at_server', 'updated_at_server']


# ==============================================================================
# 4. PROPERTY MEDIA SYNC SERIALIZER
# ==============================================================================
class PropertyMediaSyncSerializer(serializers.ModelSerializer):
    tenant_id = serializers.UUIDField(source='tenant.id', read_only=True)
    property_id = serializers.PrimaryKeyRelatedField(
        queryset=Property.objects.all(),
        source='property',
    )

    class Meta:
        model = PropertyMedia
        fields = [
            'id',
            'tenant_id',
            'property_id',
            'created_at_local',
            'created_at_server',
            'updated_at_local',
            'updated_at_server',
            'is_deleted',
            'media_type',
            'sort_order',
            'is_cover',
            'file_path',
            'remote_url',
            'thumbnail_path',
            'upload_status',
            'upload_retry_count',
            'file_size_bytes',
        ]
        read_only_fields = ['created_at_server', 'updated_at_server']


# ==============================================================================
# 5. MESSAGE SYNC SERIALIZER
# ==============================================================================
class MessageSyncSerializer(serializers.ModelSerializer):
    tenant_id = serializers.UUIDField(source='tenant.id', read_only=True)
    lead_id = serializers.PrimaryKeyRelatedField(
        queryset=Lead.objects.all(),
        source='lead',
    )

    class Meta:
        model = Message
        fields = [
            'id',
            'tenant_id',
            'lead_id',
            'created_by_user_id',
            'property_id',
            'reply_to_message_id',
            'kind',
            'prompt_type',
            'content',
            'selected_value',
            'is_action_completed',
            'attachment_local_path',
            'attachment_remote_url',
            'attachment_upload_status',
            'delivery_status',
            'is_read',
            'sent_at',
            'show_after',
            'created_at_local',
            'created_at_server',
            'updated_at_local',
            'updated_at_server',
            'is_deleted',
        ]
        read_only_fields = ['created_at_server', 'updated_at_server']


# ==============================================================================
# 6. ACTIVITY LOG SYNC SERIALIZER
# ==============================================================================
class ActivityLogSyncSerializer(serializers.ModelSerializer):
    tenant_id = serializers.UUIDField(source='tenant.id', read_only=True)

    class Meta:
        model = ActivityLog
        fields = [
            'id',
            'tenant_id',
            'agent_id',
            'lead_id',
            'message_id',
            'type',
            'occurred_at',
            'count',
            'lead_name',
            'lead_phone',
            'selected_value',
            'follow_up_date',
            'seen_at',
            'created_at_local',
            'created_at_server',
            'updated_at_local',
            'updated_at_server',
        ]
        read_only_fields = ['created_at_server', 'updated_at_server']