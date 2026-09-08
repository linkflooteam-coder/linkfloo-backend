from django.urls import path
from .views import UnifiedSyncView, MediaUploadView, RegisterDeviceView

urlpatterns = [
    # Unified Two-Way Sync Endpoint
    path('sync/', UnifiedSyncView.as_view(), name='crm_unified_sync'),
    
    # Binary Media Upload (Property Photos, Brochures, Documents)
    path('upload/', MediaUploadView.as_view(), name='crm_media_upload'),
    
    # FCM Device Token Registration Endpoint
    path('devices/register/', RegisterDeviceView.as_view(), name='register-device'),
]