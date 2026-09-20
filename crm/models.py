import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone
from accounts.models import BaseSyncModel, Tenant


# ==============================================================================
# ENUM CHOICES (1:1 with Flutter Drift Enum Ordinals)
# ==============================================================================

class TransactionType(models.IntegerChoices):
    BUY = 0, 'Buy / Sell'
    RENT = 1, 'Rent / Lease'


class PropertyCategory(models.IntegerChoices):
    RESIDENTIAL = 0, 'Residential'
    COMMERCIAL = 1, 'Commercial'


class PropertySubType(models.IntegerChoices):
    # Residential
    APARTMENT = 0, 'Apartment / Flat'
    INDEPENDENT_HOUSE = 1, 'House / Villa'
    BUILDER_FLOOR = 2, 'Builder Floor'
    PENTHOUSE = 3, 'Penthouse'
    STUDIO_APARTMENT = 4, 'Studio / 1 RK'
    RESIDENTIAL_PLOT = 5, 'Residential Plot'
    FARMHOUSE = 6, 'Farmhouse'

    # Commercial
    OFFICE_SPACE = 7, 'Office Space'
    RETAIL_SHOP = 8, 'Retail Shop'
    SHOWROOM = 9, 'Showroom'
    WAREHOUSE_GODOWN = 10, 'Warehouse / Godown'
    INDUSTRIAL_SHED = 11, 'Industrial Shed / Factory'
    COMMERCIAL_PLOT = 12, 'Commercial Plot / SCO'
    AGRICULTURAL_LAND = 13, 'Agricultural Land'
    OTHER = 14, 'Other'


class MandateType(models.IntegerChoices):
    EXCLUSIVE_MANDATE = 0, 'Exclusive Mandate'
    OPEN_LISTING = 1, 'Open Listing'


class OccupancyStatus(models.IntegerChoices):
    VACANT = 0, 'Vacant'
    OWNER_OCCUPIED = 1, 'Owner Occupied'
    TENANTED = 2, 'Tenanted (Leased)'


class FacingDirection(models.IntegerChoices):
    NORTH = 0, 'North'
    EAST = 1, 'East'
    NORTH_EAST = 2, 'North-East'
    NORTH_WEST = 3, 'North-West'
    SOUTH = 4, 'South'
    SOUTH_EAST = 5, 'South-East'
    SOUTH_WEST = 6, 'South-West'
    WEST = 7, 'West'


class FurnishingStatus(models.IntegerChoices):
    UNFURNISHED = 0, 'Unfurnished'
    SEMI_FURNISHED = 1, 'Semi-Furnished'
    FULLY_FURNISHED = 2, 'Fully Furnished'


class ParkingType(models.IntegerChoices):
    NONE = 0, 'No Parking'
    COVERED = 1, 'Covered Parking'
    OPEN = 2, 'Open Parking'
    STILT = 3, 'Stilt Parking'
    MECHANICAL = 4, 'Mechanical / Hydraulic'


class CommercialFitoutStatus(models.IntegerChoices):
    BARE_SHELL = 0, 'Bare Shell'
    WARM_SHELL = 1, 'Warm Shell'
    FULLY_FITTED_PLUG_AND_PLAY = 2, 'Plug & Play (Furnished)'


class AreaUnit(models.IntegerChoices):
    SQFT = 0, 'sq.ft.'
    SQYD_GAJ = 1, 'sq.yd. (Gaj)'
    ACRE = 2, 'Acre'
    BIGHA = 3, 'Bigha'


class PossessionStatus(models.IntegerChoices):
    READY_TO_MOVE = 0, 'Ready to Move'
    UNDER_CONSTRUCTION = 1, 'Under Construction'


class OwnershipType(models.IntegerChoices):
    FREEHOLD = 0, 'Freehold'
    LEASEHOLD = 1, 'Leasehold'
    COOPERATIVE_SOCIETY = 2, 'Co-operative Society'
    POWER_OF_ATTORNEY = 3, 'Power of Attorney (GPA)'


class KeyArrangement(models.IntegerChoices):
    WITH_OWNER = 0, 'With Owner (Call Prior)'
    WITH_SECURITY_GUARD = 1, 'With Security Guard / Caretaker'
    AT_AGENCY_OFFICE = 2, 'At Agency Office / Lockbox'
    VACANT_SELF_ACCESS = 3, 'Vacant (Self Access / Keypad)'
    TENANT_OCCUPIED_24H_NOTICE = 4, 'Tenant Occupied (24h Notice)'


class PropertyListingStatus(models.IntegerChoices):
    AVAILABLE = 0, 'Available'
    UNDER_NEGOTIATION = 1, 'Under Negotiation'
    SOLD = 2, 'Sold'
    RENTED = 3, 'Rented'
    DELISTED = 4, 'Delisted'


class PropertyVisibility(models.IntegerChoices):
    PRIVATE_LISTING = 0, 'Private Listing'
    PUBLIC_MARKETPLACE = 1, 'Public Marketplace'


class PropertyMediaType(models.IntegerChoices):
    IMAGE = 0, 'Image'
    VIDEO = 1, 'Video'
    FLOOR_PLAN = 2, 'Floor Plan'
    BROCHURE = 3, 'Brochure'


class MediaUploadStatus(models.IntegerChoices):
    PENDING = 0, 'Pending'
    UPLOADING = 1, 'Uploading'
    COMPLETED = 2, 'Completed'
    FAILED = 3, 'Failed'


class LeadWorkflowStatus(models.IntegerChoices):
    NEW_LEAD = 0, 'New Lead'
    CALLBACK = 1, 'Callback'
    INTERESTED = 2, 'Interested'
    NOT_CONNECTED = 3, 'Not Connected'
    MEETING = 4, 'Meeting'
    NEGOTIATION = 5, 'Negotiation'
    WON = 6, 'Won'
    LOST = 7, 'Lost'
    NUMBER_ISSUE = 8, 'Number Issue'


# ==============================================================================
# 1. MASTER PROJECTS / SOCIETIES
# ==============================================================================
class Project(BaseSyncModel):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='projects')
    assigned_agent_id = models.UUIDField(null=True, blank=True)

    project_name = models.CharField(max_length=200, db_index=True)
    developer_name = models.CharField(max_length=150, null=True, blank=True)
    master_rera_number = models.CharField(max_length=100, null=True, blank=True)

    total_land_area_acres = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    total_towers = models.IntegerField(null=True, blank=True)
    total_units = models.IntegerField(null=True, blank=True)
    launch_date = models.DateTimeField(null=True, blank=True)
    expected_handover_date = models.DateTimeField(null=True, blank=True)

    pincode = models.CharField(max_length=10, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    locality = models.CharField(max_length=255, null=True, blank=True)
    address_line = models.TextField(null=True, blank=True)
    landmark = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Stored as JSON arrays matching Drift StringListConverter / IntSetConverter
    standard_amenity_ids = models.JSONField(default=list, blank=True)
    custom_amenities = models.JSONField(default=list, blank=True)

    master_brochure_url = models.URLField(max_length=1000, null=True, blank=True)
    master_layout_plan_url = models.URLField(max_length=1000, null=True, blank=True)
    cover_image_url = models.URLField(max_length=1000, null=True, blank=True)

    class Meta:
        db_table = 'projects'
        indexes = [
            models.Index(fields=['tenant', 'project_name'], name='proj_name_idx'),
            models.Index(fields=['tenant', 'city', 'locality'], name='proj_location_idx'),
            models.Index(fields=['tenant', 'updated_at_server'], name='proj_sync_idx'),
        ]

    def __str__(self):
        return f"{self.project_name} ({self.city or 'Local'})"


# ==============================================================================
# 2. PROPERTIES / INVENTORY
# ==============================================================================
class Property(BaseSyncModel):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='properties')
    assigned_agent_id = models.UUIDField(null=True, blank=True)

    # Project Context
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='units')
    society_or_project_name = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    tower_block_name = models.CharField(max_length=100, null=True, blank=True)
    unit_number = models.CharField(max_length=50, null=True, blank=True)

    # Classification
    title = models.CharField(max_length=255)
    category = models.SmallIntegerField(choices=PropertyCategory.choices)
    sub_type = models.SmallIntegerField(choices=PropertySubType.choices)
    sub_type_other_label = models.CharField(max_length=100, null=True, blank=True)
    transaction_type = models.SmallIntegerField(choices=TransactionType.choices)
    mandate_type = models.SmallIntegerField(choices=MandateType.choices, default=MandateType.OPEN_LISTING)

    # Configuration & Counts
    bhk_count = models.IntegerField(null=True, blank=True)
    bathrooms_count = models.IntegerField(null=True, blank=True)
    balconies_count = models.IntegerField(null=True, blank=True)
    facing = models.SmallIntegerField(choices=FacingDirection.choices, null=True, blank=True)

    # Spatial Dimensions & Dual Area
    carpet_area = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    super_built_up_area = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    area_unit = models.SmallIntegerField(choices=AreaUnit.choices, default=AreaUnit.SQFT)
    floor_number = models.IntegerField(null=True, blank=True)
    total_floors = models.IntegerField(null=True, blank=True)
    furnishing_status = models.SmallIntegerField(choices=FurnishingStatus.choices, null=True, blank=True)

    # Parking
    parking_count = models.IntegerField(default=0)
    parking_type = models.SmallIntegerField(choices=ParkingType.choices, null=True, blank=True)

    # Commercial & Plots
    commercial_fitout = models.SmallIntegerField(choices=CommercialFitoutStatus.choices, null=True, blank=True)
    workstations_count = models.IntegerField(null=True, blank=True)
    cabins_count = models.IntegerField(null=True, blank=True)
    meeting_rooms_count = models.IntegerField(null=True, blank=True)
    road_width_feet = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    is_corner_plot = models.BooleanField(default=False)

    # Pricing & Commercials
    price_min = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    price_max = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    is_price_negotiable = models.BooleanField(default=False)
    is_all_inclusive_price = models.BooleanField(default=False)
    security_deposit_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    maintenance_charge_monthly = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    lock_in_period_months = models.IntegerField(null=True, blank=True)
    expected_rental_yield = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    # Amenities (JSON arrays)
    standard_amenity_ids = models.JSONField(default=list, blank=True)
    custom_amenities = models.JSONField(default=list, blank=True)

    # Agency Vault & Viewings (Confidential)
    occupancy_status = models.SmallIntegerField(choices=OccupancyStatus.choices, null=True, blank=True)
    owner_contact_name = models.CharField(max_length=150, null=True, blank=True)
    owner_contact_phone = models.CharField(max_length=20, null=True, blank=True)
    key_arrangement = models.SmallIntegerField(choices=KeyArrangement.choices, null=True, blank=True)
    key_contact_details = models.CharField(max_length=255, null=True, blank=True)

    # B2B Co-Broking
    is_co_broke_listing = models.BooleanField(default=False)
    co_broker_name = models.CharField(max_length=150, null=True, blank=True)
    co_broker_phone = models.CharField(max_length=20, null=True, blank=True)
    co_broker_agency = models.CharField(max_length=150, null=True, blank=True)
    commission_terms = models.CharField(max_length=100, null=True, blank=True)

    # Compliance & Title
    rera_number = models.CharField(max_length=100, null=True, blank=True)
    possession_status = models.SmallIntegerField(choices=PossessionStatus.choices, null=True, blank=True)
    possession_date = models.DateTimeField(null=True, blank=True)
    age_of_property_years = models.IntegerField(null=True, blank=True)
    ownership_type = models.SmallIntegerField(choices=OwnershipType.choices, null=True, blank=True)

    # Location & Geo
    pincode = models.CharField(max_length=10, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    locality = models.CharField(max_length=255, null=True, blank=True)
    landmark = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Description & Discovery
    description = models.TextField(null=True, blank=True)
    internal_private_notes = models.TextField(null=True, blank=True)
    listing_status = models.SmallIntegerField(choices=PropertyListingStatus.choices, default=PropertyListingStatus.AVAILABLE)
    visibility = models.SmallIntegerField(choices=PropertyVisibility.choices, default=PropertyVisibility.PRIVATE_LISTING)
    allow_platform_contact = models.BooleanField(default=True)

    class Meta:
        db_table = 'properties'
        indexes = [
            models.Index(fields=['tenant', 'updated_at_server'], name='prop_sync_idx'),
            models.Index(fields=['tenant', 'listing_status'], name='prop_status_idx'),
            models.Index(fields=['tenant', 'project'], name='prop_project_idx'),
            models.Index(fields=['tenant', 'transaction_type', 'category'], name='prop_filter_idx'),
            models.Index(fields=['tenant', 'city', 'locality'], name='prop_location_idx'),
        ]

    def __str__(self):
        return f"{self.society_or_project_name or self.title} - ₹{self.price_min or 0}"


# ==============================================================================
# 3. LEADS / CLIENT PIPELINE
# ==============================================================================
class Lead(BaseSyncModel):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='leads')

    full_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=20, db_index=True)
    email_address = models.EmailField(max_length=255, null=True, blank=True)
    avatar_url = models.URLField(max_length=1000, null=True, blank=True)

    # Client Requirements
    requirements_notes = models.TextField(null=True, blank=True)
    budget_min = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    budget_max = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)

    transaction_type = models.SmallIntegerField(choices=TransactionType.choices, null=True, blank=True)
    property_category_wanted = models.SmallIntegerField(choices=PropertyCategory.choices, null=True, blank=True)
    property_sub_type_wanted = models.SmallIntegerField(choices=PropertySubType.choices, null=True, blank=True)
    property_sub_type_other_label = models.CharField(max_length=100, null=True, blank=True)
    bhk_wanted = models.SmallIntegerField(null=True, blank=True)
    locality_wanted = models.CharField(max_length=255, null=True, blank=True)

    lead_source = models.CharField(max_length=50, default='MANUAL')
    usage_purpose = models.CharField(max_length=50, null=True, blank=True)
    timeline = models.CharField(max_length=50, null=True, blank=True)

    # Pipeline & Assignment
    workflow_status = models.SmallIntegerField(choices=LeadWorkflowStatus.choices, default=LeadWorkflowStatus.NEW_LEAD)
    next_follow_up_at = models.DateTimeField(null=True, blank=True)
    assigned_agent_id = models.UUIDField(null=True, blank=True)

    # FIXED: TextField allows storing comma-delimited UUIDs from Flutter ("id1,id2")
    linked_property_id = models.TextField(null=True, blank=True)

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
# 4. PROPERTY MEDIA / ATTACHMENTS
# ==============================================================================
class PropertyMedia(BaseSyncModel):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='property_media')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='media')

    media_type = models.SmallIntegerField(choices=PropertyMediaType.choices, default=PropertyMediaType.IMAGE)
    sort_order = models.IntegerField(default=0)
    is_cover = models.BooleanField(default=False)

    file_path = models.CharField(max_length=500, null=True, blank=True)
    remote_url = models.URLField(max_length=1000, null=True, blank=True)
    thumbnail_path = models.URLField(max_length=1000, null=True, blank=True)

    upload_status = models.SmallIntegerField(choices=MediaUploadStatus.choices, default=MediaUploadStatus.PENDING)
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
# 5. MESSAGES, ACTIVITY LOGS & DEVICES
# ==============================================================================
class Message(BaseSyncModel):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='messages')
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='messages')
    created_by_user_id = models.UUIDField()
    property_id = models.UUIDField(null=True, blank=True)
    reply_to_message_id = models.UUIDField(null=True, blank=True)

    kind = models.SmallIntegerField()
    prompt_type = models.SmallIntegerField(null=True, blank=True)
    content = models.TextField()
    selected_value = models.CharField(max_length=100, null=True, blank=True)
    is_action_completed = models.BooleanField(default=False)

    attachment_local_path = models.CharField(max_length=500, null=True, blank=True)
    attachment_remote_url = models.URLField(max_length=1000, null=True, blank=True)
    attachment_upload_status = models.SmallIntegerField(null=True, blank=True)

    delivery_status = models.SmallIntegerField(default=0)
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


class ActivityLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='activity_logs')
    agent_id = models.UUIDField()

    lead_id = models.UUIDField(null=True, blank=True)
    message_id = models.UUIDField(null=True, blank=True)

    type = models.SmallIntegerField()
    occurred_at = models.DateTimeField(default=timezone.now)
    count = models.IntegerField(null=True, blank=True)

    lead_name = models.CharField(max_length=150, null=True, blank=True)
    lead_phone = models.CharField(max_length=20, null=True, blank=True)
    selected_value = models.CharField(max_length=100, null=True, blank=True)
    follow_up_date = models.DateTimeField(null=True, blank=True)
    seen_at = models.DateTimeField(null=True, blank=True)

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
        user_identifier = (
            getattr(self.user, 'phone_number', None)
            or getattr(self.user, 'email', None)
            or str(self.user)
        )
        return f"{user_identifier} - {self.platform}"