import logging
from firebase_admin import messaging
from .models import UserDevice

logger = logging.getLogger(__name__)

def send_push_to_user(user, title, body, data=None):
    """
    Sends an FCM notification to all active devices registered to a specific user.
    Automatically deletes invalid or unregistered tokens from the database.
    """
    tokens = list(UserDevice.objects.filter(user=user).values_list('fcm_token', flat=True))
    if not tokens:
        logger.info(f"[FCM] No tokens found for user: {str(user)}")
        return 0

    # FCM data values must be strings
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