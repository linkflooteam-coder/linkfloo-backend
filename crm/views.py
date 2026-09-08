import logging
import os
import uuid

from django.conf import settings
from django.core.files.storage import default_storage
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import permissions, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView


from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import UserDevice

from .models import Lead, Property, PropertyMedia, Message, ActivityLog
from .serializers import (
    LeadSyncSerializer,
    PropertySyncSerializer,
    PropertyMediaSyncSerializer,
    MessageSyncSerializer,
    ActivityLogSyncSerializer,
)

logger = logging.getLogger(__name__)


def _sanitize_item_datetimes(data: dict) -> dict:
    """Converts naive ISO datetime strings into timezone-aware datetimes."""
    sanitized = {}
    for k, v in data.items():
        if isinstance(v, str) and ('_at' in k or '_date' in k or k == 'occurred_at'):
            parsed = parse_datetime(v)
            if parsed and timezone.is_naive(parsed):
                sanitized[k] = timezone.make_aware(parsed, timezone.get_current_timezone())
            else:
                sanitized[k] = parsed if parsed else v
        else:
            sanitized[k] = v
    return sanitized


class MediaUploadView(APIView):
    """
    Handles multipart binary uploads.
    Saves file to MEDIA_ROOT and directly links remote_url to PropertyMedia row in DB.
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        uploaded_file = (
            request.FILES.get('file') or 
            request.FILES.get('media') or 
            (next(iter(request.FILES.values())) if request.FILES else None)
        )

        if not uploaded_file:
            return Response(
                {"error": "No file uploaded under multipart key 'file' or 'media'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        tenant = getattr(request.user, 'tenant', None)
        tenant_folder = str(tenant.id) if tenant else 'general'

        # Generate collision-free filename
        ext = os.path.splitext(uploaded_file.name)[1].lower()
        unique_name = f"{uuid.uuid4()}{ext}"
        relative_path = os.path.join('properties', tenant_folder, unique_name)

        # Save to MEDIA_ROOT
        saved_path = default_storage.save(relative_path, uploaded_file)
        media_url = request.build_absolute_uri(settings.MEDIA_URL + saved_path)

        # Optional IDs passed from Flutter in FormData
        media_id = request.data.get('media_id') or request.data.get('id')
        property_id = request.data.get('property_id')

        # Directly update PropertyMedia database row
        if media_id:
            PropertyMedia.objects.filter(id=media_id, tenant=tenant).update(
                remote_url=media_url,
                file_size_bytes=uploaded_file.size,
                upload_status=2,  # completed
                updated_at_server=timezone.now(),
            )
        elif property_id:
            PropertyMedia.objects.filter(
                property_id=property_id, 
                tenant=tenant, 
                remote_url__isnull=True
            ).order_by('-created_at_local').filter(pk__in=PropertyMedia.objects.filter(
                property_id=property_id, 
                tenant=tenant, 
                remote_url__isnull=True
            ).values_list('pk', flat=True)[:1]).update(
                remote_url=media_url,
                file_size_bytes=uploaded_file.size,
                upload_status=2,
                updated_at_server=timezone.now(),
            )

        return Response({
            "url": media_url,
            "remote_url": media_url,
            "file_name": uploaded_file.name,
            "file_size_bytes": uploaded_file.size,
            "media_id": media_id,
        }, status=status.HTTP_201_CREATED)


class UnifiedSyncView(APIView):
    """
    Enterprise-Grade Atomic Two-Way Synchronization Endpoint.
    Guarantees strict tenant isolation, soft deletions, and atomic ingestion without echo loops.
    """
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        tenant = getattr(request.user, 'tenant', None)
        if not tenant:
            return Response(
                {"error": "User does not belong to any active workspace."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        client_changes = request.data.get('changes', {})
        last_sync_timestamp = request.data.get('last_sync_timestamp')

        acknowledged_ids = []

        valid_property_ids = set(
            str(pid) for pid in Property.objects.filter(tenant=tenant).values_list('id', flat=True)
        )
        valid_lead_ids = set(
            str(lid) for lid in Lead.objects.filter(tenant=tenant).values_list('id', flat=True)
        )

        now = timezone.now()

        # ---------------------------------------------------------------------
        # 1. Ingest Properties
        # ---------------------------------------------------------------------
        for item in client_changes.get('properties', []):
            prop_id = item.get('id')
            if not prop_id:
                continue

            if item.get('is_deleted') is True:
                Property.objects.filter(id=prop_id, tenant=tenant).update(
                    is_deleted=True,
                    updated_at_server=now,
                )
                acknowledged_ids.append(str(prop_id))
                continue

            item_data = {
                k: v for k, v in item.items()
                if k not in ['id', 'tenant_id', 'created_at_server', 'updated_at_server']
            }
            item_data = _sanitize_item_datetimes(item_data)

            Property.objects.update_or_create(
                id=prop_id,
                tenant=tenant,
                defaults={**item_data, 'tenant': tenant},
            )
            valid_property_ids.add(str(prop_id))
            acknowledged_ids.append(str(prop_id))

        # ---------------------------------------------------------------------
        # 2. Ingest Leads
        # ---------------------------------------------------------------------
        for item in client_changes.get('leads', []):
            lead_id = item.get('id')
            if not lead_id:
                continue

            if item.get('is_deleted') is True:
                Lead.objects.filter(id=lead_id, tenant=tenant).update(
                    is_deleted=True,
                    updated_at_server=now,
                )
                acknowledged_ids.append(str(lead_id))
                continue

            item_data = {
                k: v for k, v in item.items()
                if k not in ['id', 'tenant_id', 'created_at_server', 'updated_at_server']
            }

            linked_prop = item_data.get('linked_property_id')
            if linked_prop and str(linked_prop) not in valid_property_ids:
                item_data['linked_property_id'] = None

            if not item_data.get('assigned_agent_id'):
                item_data['assigned_agent_id'] = request.user.id

            item_data = _sanitize_item_datetimes(item_data)

            Lead.objects.update_or_create(
                id=lead_id,
                tenant=tenant,
                defaults={**item_data, 'tenant': tenant},
            )
            valid_lead_ids.add(str(lead_id))
            acknowledged_ids.append(str(lead_id))

        # ---------------------------------------------------------------------
        # 3. Ingest Property Media
        # ---------------------------------------------------------------------
        for item in client_changes.get('property_media', []):
            media_id = item.get('id')
            property_id = item.get('property_id')
            if not media_id:
                continue

            if item.get('is_deleted') is True:
                PropertyMedia.objects.filter(id=media_id, tenant=tenant).update(
                    is_deleted=True,
                    updated_at_server=now,
                )
                acknowledged_ids.append(str(media_id))
                continue

            if not property_id or str(property_id) not in valid_property_ids:
                continue

            item_data = {
                k: v for k, v in item.items()
                if k not in ['id', 'tenant_id', 'property_id', 'created_at_server', 'updated_at_server']
            }
            item_data = _sanitize_item_datetimes(item_data)

            PropertyMedia.objects.update_or_create(
                id=media_id,
                tenant=tenant,
                property_id=property_id,
                defaults={**item_data, 'tenant': tenant, 'property_id': property_id},
            )
            acknowledged_ids.append(str(media_id))

        # ---------------------------------------------------------------------
        # 4. Ingest Messages
        # ---------------------------------------------------------------------
        for item in client_changes.get('messages', []):
            msg_id = item.get('id')
            lead_id = item.get('lead_id')
            if not msg_id:
                continue

            if item.get('is_deleted') is True:
                Message.objects.filter(id=msg_id, tenant=tenant).update(
                    is_deleted=True,
                    updated_at_server=now,
                )
                acknowledged_ids.append(str(msg_id))
                continue

            if not lead_id or str(lead_id) not in valid_lead_ids:
                continue

            item_data = {
                k: v for k, v in item.items()
                if k not in ['id', 'tenant_id', 'lead_id', 'created_at_server', 'updated_at_server']
            }
            item_data = _sanitize_item_datetimes(item_data)

            Message.objects.update_or_create(
                id=msg_id,
                tenant=tenant,
                lead_id=lead_id,
                defaults={**item_data, 'tenant': tenant, 'lead_id': lead_id},
            )
            acknowledged_ids.append(str(msg_id))

        # ---------------------------------------------------------------------
        # 5. Ingest Activity Logs
        # ---------------------------------------------------------------------
        for item in client_changes.get('activity_logs', []):
            act_id = item.get('id')
            if not act_id:
                continue

            if item.get('is_deleted') is True:
                ActivityLog.objects.filter(id=act_id, tenant=tenant).delete()
                acknowledged_ids.append(str(act_id))
                continue

            item_data = {
                k: v for k, v in item.items()
                if k not in ['id', 'tenant_id', 'created_at_server', 'updated_at_server']
            }

            lead_id = item_data.get('lead_id')
            if lead_id and str(lead_id) not in valid_lead_ids:
                item_data['lead_id'] = None

            prop_id = item_data.get('property_id')
            if prop_id and str(prop_id) not in valid_property_ids:
                item_data['property_id'] = None

            item_data = _sanitize_item_datetimes(item_data)

            ActivityLog.objects.update_or_create(
                id=act_id,
                tenant=tenant,
                defaults={**item_data, 'tenant': tenant},
            )
            acknowledged_ids.append(str(act_id))

        # =====================================================================
        # PHASE 2: CALCULATE SERVER DELTAS
        # =====================================================================
        server_sync_timestamp = timezone.now()

        since_time = parse_datetime(last_sync_timestamp) if last_sync_timestamp else None

        leads_qs = Lead.objects.filter(tenant=tenant)
        props_qs = Property.objects.filter(tenant=tenant)
        media_qs = PropertyMedia.objects.filter(tenant=tenant)
        msgs_qs = Message.objects.filter(tenant=tenant)
        acts_qs = ActivityLog.objects.filter(tenant=tenant)

        if since_time:
            leads_qs = leads_qs.filter(updated_at_server__gt=since_time)
            props_qs = props_qs.filter(updated_at_server__gt=since_time)
            media_qs = media_qs.filter(updated_at_server__gt=since_time)
            msgs_qs = msgs_qs.filter(updated_at_server__gt=since_time)
            acts_qs = acts_qs.filter(updated_at_server__gt=since_time)

        if acknowledged_ids:
            leads_qs = leads_qs.exclude(id__in=acknowledged_ids)
            props_qs = props_qs.exclude(id__in=acknowledged_ids)
            media_qs = media_qs.exclude(id__in=acknowledged_ids)
            msgs_qs = msgs_qs.exclude(id__in=acknowledged_ids)
            acts_qs = acts_qs.exclude(id__in=acknowledged_ids)

        return Response({
            "server_timestamp": server_sync_timestamp.isoformat(),
            "acknowledged_ids": acknowledged_ids,
            "deltas": {
                "leads": LeadSyncSerializer(leads_qs, many=True).data,
                "properties": PropertySyncSerializer(props_qs, many=True).data,
                "property_media": PropertyMediaSyncSerializer(media_qs, many=True).data,
                "messages": MessageSyncSerializer(msgs_qs, many=True).data,
                "activity_logs": ActivityLogSyncSerializer(acts_qs, many=True).data,
            }
        }, status=status.HTTP_200_OK)


class RegisterDeviceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        fcm_token = request.data.get('fcm_token')
        platform = request.data.get('platform', 'android')

        if not fcm_token:
            return Response({'error': 'fcm_token is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Update or create device record for this user
        UserDevice.objects.update_or_create(
            fcm_token=fcm_token,
            defaults={'user': request.user, 'platform': platform}
        )

        return Response({'status': 'device registered successfully'}, status=status.HTTP_200_OK)