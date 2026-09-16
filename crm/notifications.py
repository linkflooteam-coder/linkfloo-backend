import os
import logging
import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings
from .models import UserDevice

logger = logging.getLogger(__name__)

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


def _clean_stale_tokens(tokens, responses):
    for idx, resp in enumerate(responses):
        if not resp.success:
            bad_token = tokens[idx]
            err_str = str(resp.exception)
            if any(k in err_str for k in ("NOT_FOUND", "UNREGISTERED", "INVALID_ARGUMENT")):
                UserDevice.objects.filter(fcm_token=bad_token).delete()
                logger.info(f"[FCM] Removed stale token: {bad_token[:12]}...")


def send_lead_reminder_push(user, lead, status_tag="Follow-up Due", custom_message=None):
    """
    Constructs a high-priority data push strictly using Lead model fields.
    """
    tokens = list(UserDevice.objects.filter(user=user).values_list('fcm_token', flat=True))
    if not tokens:
        logger.info(f"[FCM] No tokens registered for user: {str(user)}")
        return 0

    # 1. Header Title: Name first, phone number fallback
    has_name = bool(lead.full_name and lead.full_name.strip())
    contact_title = lead.full_name.strip() if has_name else str(lead.phone_number)

    # 2. Extract specs from Lead table fields
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

    # 3. Context note: requirements_notes -> last_message_preview fallback
    notes = ""
    if lead.requirements_notes and lead.requirements_notes.strip():
        notes = lead.requirements_notes.strip()
    elif getattr(lead, 'last_message_preview', None) and lead.last_message_preview.strip():
        notes = lead.last_message_preview.strip()

    if custom_message:
        detailed_body = custom_message
    elif notes and specs_line:
        detailed_body = f'📝 "{notes}"\n📍 {specs_line}'
    elif notes:
        detailed_body = f'📝 "{notes}"'
    elif specs_line:
        detailed_body = f'📍 {specs_line}'
    else:
        detailed_body = f"Scheduled reminder for {contact_title}"

    # 4. Pure DATA payload (Prevents Android duplicate notifications)
    payload_data = {
        'type': 'lead_reminder',
        'lead_id': str(lead.id),
        'contact_name': str(contact_title),
        'status_tag': str(status_tag),
        'detailed_notes': str(detailed_body),
        'click_action': 'FLUTTER_NOTIFICATION_CLICK',
    }

    message = messaging.MulticastMessage(
        data=payload_data,
        android=messaging.AndroidConfig(
            priority='high',
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
        logger.error(f"[FCM] Dispatch error: {e}")
        return 0