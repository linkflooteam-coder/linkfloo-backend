import os
import logging
import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings
from .models import UserDevice

logger = logging.getLogger(__name__)

# Auto-initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred_path = os.path.join(settings.BASE_DIR, 'firebase-service-account.json')
    if not os.path.exists(cred_path):
        cred_path = os.path.join(os.path.dirname(settings.BASE_DIR), 'firebase-service-account.json')

    if os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        logger.info(f"[Firebase] Initialized with credentials: {cred_path}")
    else:
        firebase_admin.initialize_app()
        logger.warning("[Firebase] Credential file not found, fell back to default.")


def _clean_stale_tokens(tokens, responses):
    """Deletes unregistered or invalid device tokens from the database."""
    for idx, resp in enumerate(responses):
        if not resp.success:
            bad_token = tokens[idx]
            err_str = str(resp.exception)
            if any(k in err_str for k in ("NOT_FOUND", "UNREGISTERED", "INVALID_ARGUMENT")):
                UserDevice.objects.filter(fcm_token=bad_token).delete()
                logger.info(f"[FCM] Removed invalid device token: {bad_token[:12]}...")


def send_push_to_user(user, title, body, data=None):
    """
    Sends a general FCM push notification to all active devices of a user.
    """
    tokens = list(UserDevice.objects.filter(user=user).values_list('fcm_token', flat=True))
    if not tokens:
        logger.info(f"[FCM] No tokens found for user: {str(user)}")
        return 0

    payload_data = {k: str(v) for k, v in (data or {}).items()}
    payload_data.setdefault('title', str(title))
    payload_data.setdefault('body', str(body))
    payload_data.setdefault('contact_name', str(title))
    payload_data.setdefault('detailed_notes', str(body))
    payload_data.setdefault('status_tag', 'Follow-up Due')

    message = messaging.MulticastMessage(
        notification=messaging.Notification(title=title, body=body),
        data=payload_data,
        android=messaging.AndroidConfig(
            priority='high',
            notification=messaging.AndroidNotification(
                channel_id='linkfloo_reminders',
                priority='max',
                default_sound=True,
            ),
        ),
        tokens=tokens,
    )

    try:
        response = messaging.send_each_for_multicast(message)
        logger.info(f"[FCM] Sent {response.success_count}/{len(tokens)} to {str(user)}")
        if response.failure_count > 0:
            _clean_stale_tokens(tokens, response.responses)
        return response.success_count
    except Exception as e:
        logger.error(f"[FCM] General dispatch error: {e}")
        return 0


def send_lead_reminder_push(user, lead, status_tag="Follow-up Due", custom_message=None):
    """
    Constructs and sends a WhatsApp-style lead card notification with specs and past notes.
    Guarantees that contact name and phone number never duplicate.
    """
    tokens = list(UserDevice.objects.filter(user=user).values_list('fcm_token', flat=True))
    if not tokens:
        logger.info(f"[FCM] No tokens found for user: {str(user)}")
        return 0

    # 1. Primary Title: STRICTLY Name if available; otherwise Phone Number (never both)
    has_name = bool(lead.full_name and lead.full_name.strip())
    contact_title = lead.full_name.strip() if has_name else str(lead.phone_number)

    # 2. Extract and format property specs (BHK • Type • Locality • Budget)
    specs = []
    if getattr(lead, 'bhk_wanted', None):
        specs.append(str(lead.bhk_wanted))
    if getattr(lead, 'property_category_wanted', None):
        specs.append(str(lead.property_category_wanted))
    if getattr(lead, 'locality_wanted', None) and lead.locality_wanted.strip():
        specs.append(lead.locality_wanted.strip())
    if getattr(lead, 'budget_max', None) and lead.budget_max > 0:
        specs.append(f"₹{lead.budget_max}")
    specs_line = " • ".join(specs)

    # 3. Format past conversation notes without repeating phone number or name
    notes = lead.requirements_notes.strip() if (lead.requirements_notes and lead.requirements_notes.strip()) else ""

    if custom_message:
        detailed_body = custom_message
    elif notes and specs_line:
        detailed_body = f'📝 "{notes}"\n📍 {specs_line}'
    elif notes:
        detailed_body = f'📝 "{notes}"'
    elif specs_line:
        detailed_body = f'📍 {specs_line}'
    else:
        detailed_body = "Tap to view conversation & details"

    # 4. Supply both legacy ('title', 'body') and new ('contact_name', 'detailed_notes') keys
    # This prevents the open app from falling back to "Linkfloo CRM / New update received"
    payload_data = {
        'lead_id': str(lead.id),
        'title': str(contact_title),
        'body': str(detailed_body),
        'contact_name': str(contact_title),
        'status_tag': str(status_tag),
        'detailed_notes': str(detailed_body),
        'click_action': 'FLUTTER_NOTIFICATION_CLICK',
    }

    message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title=contact_title,
            body=detailed_body,
        ),
        data=payload_data,
        android=messaging.AndroidConfig(
            priority='high',
            notification=messaging.AndroidNotification(
                channel_id='linkfloo_reminders',
                priority='max',
                default_sound=True,
            ),
        ),
        tokens=tokens,
    )

    try:
        response = messaging.send_each_for_multicast(message)
        logger.info(f"[FCM] Sent lead reminder {response.success_count}/{len(tokens)} to {str(user)}")
        if response.failure_count > 0:
            _clean_stale_tokens(tokens, response.responses)
        return response.success_count
    except Exception as e:
        logger.error(f"[FCM] Lead reminder dispatch error: {e}")
        return 0