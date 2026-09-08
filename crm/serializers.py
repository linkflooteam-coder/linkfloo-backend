from rest_framework import serializers
from .models import Lead, Property, PropertyMedia, Message, ActivityLog


class LeadSyncSerializer(serializers.ModelSerializer):
    tenant_id = serializers.UUIDField(source='tenant.id', read_only=True)

    class Meta:
        model = Lead
        fields = [
            'id', 'tenant_id', 'created_at_local', 'created_at_server',
            'updated_at_local', 'updated_at_server', 'is_deleted',
            'full_name', 'phone_number', 'email_address', 'avatar_url',
            'requirements_notes', 'budget_min', 'budget_max',
            'transaction_type', 'property_category_wanted', 'property_sub_type_wanted',
            'property_sub_type_other_label', 'bhk_wanted', 'locality_wanted',
            'lead_source', 'usage_purpose', 'timeline', 'workflow_status',
            'next_follow_up_at', 'assigned_agent_id', 'linked_property_id',
            'last_message_preview', 'last_message_at', 'unread_messages_count'
        ]
        read_only_fields = ['created_at_server', 'updated_at_server']


class PropertySyncSerializer(serializers.ModelSerializer):
    tenant_id = serializers.UUIDField(source='tenant.id', read_only=True)

    class Meta:
        model = Property
        fields = [
            'id', 'tenant_id', 'assigned_agent_id',
            'created_at_local', 'created_at_server', 'updated_at_local', 'updated_at_server',
            'is_deleted', 'title', 'category', 'sub_type', 'sub_type_other_label',
            'transaction_type', 'bhk', 'area_value', 'area_unit', 'furnishing_status',
            'floor_number', 'total_floors', 'price_min', 'price_max',
            'is_price_negotiable', 'security_deposit_amount', 'maintenance_charge_monthly',
            'rera_number', 'possession_status', 'possession_date', 'pincode',
            'city', 'state', 'locality', 'landmark', 'latitude', 'longitude',
            'owner_contact_name', 'owner_contact_phone', 'listing_status',
            'visibility', 'allow_platform_contact', 'description', 'amenities_notes'
        ]
        read_only_fields = ['created_at_server', 'updated_at_server']


class PropertyMediaSyncSerializer(serializers.ModelSerializer):
    tenant_id = serializers.UUIDField(source='tenant.id', read_only=True)
    property_id = serializers.UUIDField(source='property.id')

    class Meta:
        model = PropertyMedia
        fields = [
            'id', 'tenant_id', 'property_id',
            'created_at_local', 'created_at_server', 'updated_at_local', 'updated_at_server',
            'is_deleted', 'media_type', 'sort_order', 'is_cover', 'file_path',
            'remote_url', 'thumbnail_path', 'upload_status', 'upload_retry_count',
            'file_size_bytes'
        ]
        read_only_fields = ['created_at_server', 'updated_at_server']


class MessageSyncSerializer(serializers.ModelSerializer):
    tenant_id = serializers.UUIDField(source='tenant.id', read_only=True)
    lead_id = serializers.UUIDField(source='lead.id')

    class Meta:
        model = Message
        fields = [
            'id', 'tenant_id', 'lead_id', 'created_by_user_id', 'property_id',
            'reply_to_message_id', 'kind', 'prompt_type', 'content', 'selected_value',
            'is_action_completed', 'attachment_local_path', 'attachment_remote_url',
            'attachment_upload_status', 'delivery_status', 'is_read', 'sent_at',
            'show_after', 'created_at_local', 'created_at_server', 'updated_at_local',
            'updated_at_server', 'is_deleted'
        ]
        read_only_fields = ['created_at_server', 'updated_at_server']


class ActivityLogSyncSerializer(serializers.ModelSerializer):
    tenant_id = serializers.UUIDField(source='tenant.id', read_only=True)

    class Meta:
        model = ActivityLog
        fields = [
            'id', 'tenant_id', 'agent_id', 'lead_id', 'message_id', 'type',
            'occurred_at', 'count', 'lead_name', 'lead_phone', 'selected_value',
            'follow_up_date', 'seen_at', 'created_at_local', 'created_at_server',
            'updated_at_local', 'updated_at_server'
        ]
        read_only_fields = ['created_at_server', 'updated_at_server']