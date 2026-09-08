from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # 1. Accounts: Auth, Profile, Team, and Workspace Branding
    # Resolves:
    # /api/auth/firebase/
    # /api/auth/jwt/refresh/
    # /api/users/me/
    # /api/users/team/
    # /api/workspace/
    # /api/workspace/rotate-invite/
    path('api/', include('accounts.urls')),

    # 2. CRM: Offline-First Two-Way Sync Engine (Leads, Properties, Messages, Activities)
    # Resolves:
    # /api/crm/sync/
    path('api/crm/', include('crm.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)