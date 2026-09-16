import os
import json
import logging
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from crm.models import Lead, UserDevice
from crm.notifications import send_lead_reminder_push

logger = logging.getLogger(__name__)

SENT_LOG_FILE = os.path.join(settings.BASE_DIR, '.cron_sent_log.json')


def _load_sent_log():
    if os.path.exists(SENT_LOG_FILE):
        try:
            with open(SENT_LOG_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _save_sent_log(log_data):
    # Prune entries older than 48 hours to keep log lightweight
    cutoff = (timezone.now() - timedelta(hours=48)).isoformat()
    pruned = {k: v for k, v in log_data.items() if v > cutoff}
    try:
        with open(SENT_LOG_FILE, 'w') as f:
            json.dump(pruned, f)
    except Exception as e:
        logger.error(f"[Cron] Error saving sent log: {e}")


class Command(BaseCommand):
    help = "Scans leads and dispatches automated WhatsApp-style follow-up pushes"

    def handle(self, *args, **options):
        now = timezone.now()
        sent_log = _load_sent_log()
        dispatched_count = 0

        active_leads = Lead.objects.filter(
            next_follow_up_at__isnull=False,
            is_deleted=False
        ).exclude(workflow_status__in=[6, 7])  # Exclude Won (6) and Lost (7)

        for lead in active_leads:
            follow_up = lead.next_follow_up_at
            status = getattr(lead, 'workflow_status', 0)

            user = getattr(lead, 'assigned_agent', None) or getattr(lead, 'user', None)
            if not user:
                device = UserDevice.objects.first()
                if device:
                    user = device.user

            if not user:
                continue

            # 1. Meeting Alert: T - 15 Minutes
            if status == 4:  # LeadStatus.meeting
                t15_target = follow_up - timedelta(minutes=15)
                if (now - timedelta(minutes=1)) <= t15_target <= (now + timedelta(minutes=1)):
                    key = f"{lead.id}_m15_{follow_up.isoformat()}"
                    if key not in sent_log:
                        success = send_lead_reminder_push(
                            user=user,
                            lead=lead,
                            status_tag="Meeting • In 15m",
                            custom_message="⏳ Site visit / meeting starts in 15 minutes. Get ready!"
                        )
                        if success:
                            sent_log[key] = now.isoformat()
                            dispatched_count += 1
                            self.stdout.write(self.style.SUCCESS(f"Sent T-15m Meeting alert for lead {lead.id}"))

            # 2. Exact Due Alert: T - 0 (Callbacks & Meetings)
            if (now - timedelta(minutes=1, seconds=30)) <= follow_up <= (now + timedelta(seconds=45)):
                key = f"{lead.id}_m0_{follow_up.isoformat()}"
                if key not in sent_log:
                    if status == 4:
                        tag = "Meeting • Starting Now"
                        msg = "🚨 Your scheduled meeting is starting right now!"
                    elif status == 1:
                        tag = "Callback Due"
                        msg = None
                    else:
                        tag = "Follow-up Due"
                        msg = None

                    success = send_lead_reminder_push(
                        user=user,
                        lead=lead,
                        status_tag=tag,
                        custom_message=msg
                    )
                    if success:
                        sent_log[key] = now.isoformat()
                        dispatched_count += 1
                        self.stdout.write(self.style.SUCCESS(f"Sent T-0 alert ({tag}) for lead {lead.id}"))

        _save_sent_log(sent_log)
        self.stdout.write(f"Cron complete. Dispatched: {dispatched_count}")