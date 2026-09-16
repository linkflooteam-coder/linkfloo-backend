import os
import logging
import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings
from .models import UserDevice

logger = logging.getLogger(__name__)

# Auto-initialize Firebase Admin SDK if not already active
if not firebase_admin._apps:
    cred_path = os.path.join(settings.BASE_DIR, 'firebase-service-account.json')
    if os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        logger.info(f"[Firebase] Initialized with credentials: {cred_path}")
    else:
        firebase_admin.initialize_app()
        logger.warning(f"[Firebase] Credential file not found at {cred_path}, fell back to default.")


def send_push_to_user(user, title, body, data=None):
    """
    Sends an FCM notification to all active devices registered to a specific user.
    Automatically deletes invalid or unregistered tokens from the database.
    """
    tokens = list(UserDevice.objects.filter(user=user).values_list('fcm_token', flat=True))
    if not tokens:
        logger.info(f"[FCM] No tokens found for user: {str(user)}")
        return 0

    payload_data = {k: str(v) for k, v in (data or {}).items()}

    message = messaging.MulticastMessage(
        notification=messaging.Notification(title=title, body=body),
        data=payload_data,
        tokens=tokens,
    )

    try:
        response = messaging.send_each_for_multicast(message)
        logger.info(f"[FCM] Sent {response.success_count}/{len(tokens)} to {str(user)}")

        if response.failure_count > 0:
            for idx, resp in enumerate(response.responses):
                if not resp.success:
                    bad_token = tokens[idx]
                    err_str = str(resp.exception)
                    if "NOT_FOUND" in err_str or "UNREGISTERED" in err_str:
                        UserDevice.objects.filter(fcm_token=bad_token).delete()
                        logger.info(f"[FCM] Deleted stale token: {bad_token[:12]}...")

        return response.success_count
    except Exception as e:
        logger.error(f"[FCM] Dispatch error: {e}")
        return 0