import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'linkfloo_backend.settings')
django.setup()

import firebase_admin
from firebase_admin import credentials, messaging
from crm.models import UserDevice

if not firebase_admin._apps:
    cred = credentials.Certificate(r"C:\Users\deepak\Desktop\linkFloo_Django\linkfloo_backend\firebase-service-account.json")
    firebase_admin.initialize_app(cred)

device = UserDevice.objects.first()
if device:
    # Send a data-only payload so Flutter controls the notification display entirely
    message = messaging.Message(
        data={
            'title': 'Linkfloo CRM Test',
            'body': 'Pipeline is fully operational!',
            'lead_id': '12345'
        },
        token=device.fcm_token
    )
    response = messaging.send(message)
    print(f"Successfully sent message: {response}")
else:
    print("No registered devices found.")