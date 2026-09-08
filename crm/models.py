import uuid
from django.db import models
from django.utils import timezone
from accounts.models import BaseSyncModel, Tenant
from django.conf import settings


# ==============================================================================
# 1. LEADS / CLIENT PIPELINE
# ==============================================================================
class Lead(BaseSyncModel):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='leads')

    full_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=20)
    email_address = models.EmailField(max_length=255, null=True, blank=True)
    avatar_url = models.URLField(max_length=1000, null=True, blank=True)

    # Client Requirements
    requirements_notes = models.TextField(null=True, blank=True)
    budget_min = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    budget_max = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)

    transaction_type = models.SmallIntegerField(null=True, blank=True)  # Buy(0), Rent(1)
    property_category_wanted = models.SmallIntegerField(null=True, blank=True)
    property_sub_type_wanted = models.SmallIntegerField(null=True, blank=True)
    property_sub_type_other_label = models.CharField(max_length=100, null=True, blank=True)
    bhk_wanted = models.SmallIntegerField(null=True, blank=True)
    locality_wanted = models.CharField(max_length=255, null=True, blank=True)

    lead_source = models.CharField(max_length=50, default='MANUAL')
    usage_purpose = models.CharField(max_length=50, null=True, blank=True)
    timeline = models.CharField(max_length=50, null=True, blank=True)

    # Pipeline & Assignment
    workflow_status = models.SmallIntegerField(default=0)  # New, Contacted, Site Visit, Won, Lost
    next_follow_up_at = models.DateTimeField(null=True, blank=True)
    assigned_agent_id = models.UUIDField(null=True, blank=True)
    linked_property_id = models.UUIDField(null=True, blank=True)

    # Chat & Feed Caching
    last_message_preview = models.TextField(null=True, blank=True)
    last_message_at = models.DateTimeField(null=True, blank=True)
    unread_messages_count = models.IntegerField(default=0)

    class Meta:
        db_table = 'leads'
        indexes = [
            models.Index(fields=['tenant', 'updated_at_server'], name='leads_sync_idx'),
            models.Index(fields=['tenant', 'workflow_status'], name='leads_status_idx'),
            models.Index(fields=['tenant', 'next_follow_up_at'], name='leads_followup_idx'),
            models.Index(fields=['tenant', 'phone_number'], name='leads_phone_idx'),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.phone_number})"


# ==============================================================================
# 2. PROPERTIES / INVENTORY
# ==============================================================================
class Property(BaseSyncModel):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='properties')
    assigned_agent_id = models.UUIDField(null=True, blank=True)

    # Classification
    title = models.CharField(max_length=255)
    category = models.SmallIntegerField()       # Residential(0), Commercial(1), Plot(2), Industrial(3)
    sub_type = models.SmallIntegerField()       # Apartment, Villa, Plot, Office, etc.
    sub_type_other_label = models.CharField(max_length=100, null=True, blank=True)
    transaction_type = models.SmallIntegerField()  # Sell(0), Rent(1)
    bhk = models.SmallIntegerField(null=True, blank=True)

    # Specifications & Measurements
    area_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    area_unit = models.SmallIntegerField(default=0)  # sqft(0), sqyd_gaj(1), acre(2), bigha(3)
    furnishing_status = models.SmallIntegerField(null=True, blank=True)
    floor_number = models.IntegerField(null=True, blank=True)
    total_floors = models.IntegerField(null=True, blank=True)

    # Financials
    price_min = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    price_max = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    is_price_negotiable = models.BooleanField(default=False)
    security_deposit_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    maintenance_charge_monthly = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Compliance & Timeline
    rera_number = models.CharField(max_length=100, null=True, blank=True)
    possession_status = models.SmallIntegerField(null=True, blank=True)  # Ready to Move, Under Construction
    possession_date = models.DateTimeField(null=True, blank=True)

    # Location & Geo
    pincode = models.CharField(max_length=10, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    locality = models.CharField(max_length=255, null=True, blank=True)
    landmark = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Owner Records (Confidential)
    owner_contact_name = models.CharField(max_length=150, null=True, blank=True)
    owner_contact_phone = models.CharField(max_length=20, null=True, blank=True)

    # Lifecycle & Discovery
    listing_status = models.SmallIntegerField(default=0)  # Available(0), Under Offer(1), Sold(2)
    visibility = models.SmallIntegerField(default=0)      # Private(0), Public/Marketplace(1)
    allow_platform_contact = models.BooleanField(default=True)

    description = models.TextField(null=True, blank=True)
    amenities_notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'properties'
        indexes = [
            models.Index(fields=['tenant', 'updated_at_server'], name='prop_sync_idx'),
            models.Index(fields=['tenant', 'listing_status'], name='prop_status_idx'),
            models.Index(fields=['tenant', 'transaction_type', 'category'], name='prop_filter_idx'),
            models.Index(fields=['tenant', 'city', 'locality'], name='prop_location_idx'),
        ]

    def __str__(self):
        return f"{self.title} - ₹{self.price_min or 0}"


# ==============================================================================
# 3. PROPERTY MEDIA / S3 ATTACHMENTS
# ==============================================================================
class PropertyMedia(BaseSyncModel):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='property_media')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='media')

    media_type = models.SmallIntegerField(default=0)  # Image(0), Video(1), FloorPlan(2)
    sort_order = models.IntegerField(default=0)
    is_cover = models.BooleanField(default=False)

    file_path = models.CharField(max_length=500, null=True, blank=True)
    remote_url = models.URLField(max_length=1000, null=True, blank=True)
    thumbnail_path = models.URLField(max_length=1000, null=True, blank=True)

    upload_status = models.SmallIntegerField(default=0)  # pending(0), uploading(1), completed(2), failed(3)
    upload_retry_count = models.IntegerField(default=0)
    file_size_bytes = models.BigIntegerField(null=True, blank=True)

    class Meta:
        db_table = 'property_media'
        indexes = [
            models.Index(fields=['tenant', 'property', 'sort_order'], name='media_gallery_idx'),
            models.Index(fields=['property', 'is_cover'], name='media_cover_idx'),
            models.Index(fields=['tenant', 'updated_at_server'], name='media_sync_idx'),
        ]

    def __str__(self):
        return f"Media for {self.property_id} (Cover: {self.is_cover})"


# ==============================================================================
# 4. MESSAGES & INTERACTIVE QUICK-DOCK
# ==============================================================================
class Message(BaseSyncModel):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='messages')
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='messages')
    created_by_user_id = models.UUIDField()
    property_id = models.UUIDField(null=True, blank=True)
    reply_to_message_id = models.UUIDField(null=True, blank=True)

    kind = models.SmallIntegerField()  # systemNotice, systemPrompt, agentReply, agentNote, leadReply
    prompt_type = models.SmallIntegerField(null=True, blank=True)
    content = models.TextField()
    selected_value = models.CharField(max_length=100, null=True, blank=True)
    is_action_completed = models.BooleanField(default=False)

    attachment_local_path = models.CharField(max_length=500, null=True, blank=True)
    attachment_remote_url = models.URLField(max_length=1000, null=True, blank=True)
    attachment_upload_status = models.SmallIntegerField(null=True, blank=True)

    delivery_status = models.SmallIntegerField(default=0)  # pending=0, sent=1, delivered=2, read=3
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(default=timezone.now)
    show_after = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'messages'
        indexes = [
            models.Index(fields=['tenant', 'lead', 'sent_at'], name='msg_lead_thread_idx'),
            models.Index(fields=['tenant', 'lead', 'is_read'], name='msg_lead_unread_idx'),
            models.Index(fields=['tenant', 'show_after'], name='msg_time_release_idx'),
            models.Index(fields=['tenant', 'updated_at_server'], name='msg_sync_delta_idx'),
        ]

    def __str__(self):
        return f"Msg from {self.created_by_user_id} on Lead {self.lead_id}"


# ==============================================================================
# 5. ACTIVITY LOGS (IMMUTABLE AUDIT TRAIL)
# ==============================================================================
class ActivityLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='activity_logs')
    agent_id = models.UUIDField()

    lead_id = models.UUIDField(null=True, blank=True)
    message_id = models.UUIDField(null=True, blank=True)

    type = models.SmallIntegerField()  # call, whatsapp, siteVisit, statusChange, note, batchImport
    occurred_at = models.DateTimeField(default=timezone.now)
    count = models.IntegerField(null=True, blank=True)

    # Immutable Historical Snapshot
    lead_name = models.CharField(max_length=150, null=True, blank=True)
    lead_phone = models.CharField(max_length=20, null=True, blank=True)

    # Outcome & Story Unseen Ring
    selected_value = models.CharField(max_length=100, null=True, blank=True)
    follow_up_date = models.DateTimeField(null=True, blank=True)
    seen_at = models.DateTimeField(null=True, blank=True)

    # Sync Bookkeeping
    created_at_local = models.DateTimeField(default=timezone.now)
    created_at_server = models.DateTimeField(auto_now_add=True)
    updated_at_local = models.DateTimeField(default=timezone.now)
    updated_at_server = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'activity_logs'
        indexes = [
            models.Index(fields=['tenant', 'occurred_at'], name='act_feed_idx'),
            models.Index(fields=['tenant', 'agent_id', 'seen_at', 'occurred_at'], name='act_ring_idx'),
            models.Index(fields=['tenant', 'lead_id', 'occurred_at'], name='act_lead_timeline_idx'),
            models.Index(fields=['tenant', 'updated_at_server'], name='act_sync_idx'),
        ]

    def __str__(self):
        return f"Activity {self.type} by {self.agent_id} at {self.occurred_at}"

# ==============================================================================
# 6. Notification Service
# ==============================================================================

class UserDevice(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='devices')
    fcm_token = models.TextField(unique=True)
    platform = models.CharField(max_length=20, default='android')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.platform}"