import asyncio
import json

import firebase_admin
from firebase_admin import credentials, messaging

firebase_admin.initialize_app(credentials.Certificate("./serviceAccountKey.json"))


def send_notification(data, deviceToken):
    def _send_notification():
        try:
            messaging.send(messaging.Message({"json": json.dumps(data)}, token=deviceToken))

        except Exception as e:
            print(e)

    return asyncio.to_thread(_send_notification)
