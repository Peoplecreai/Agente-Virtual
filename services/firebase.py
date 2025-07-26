import os
import logging
from typing import Any
import firebase_admin
from firebase_admin import credentials, firestore

logger = logging.getLogger(__name__)

class FirebaseService:
    def __init__(self):
        creds_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT")
        if not creds_json:
            logger.warning("GOOGLE_SERVICE_ACCOUNT not set; Firebase disabled")
            self.client = None
            return
        cred = credentials.Certificate(creds_json)
        firebase_admin.initialize_app(cred)
        self.client = firestore.client()

    def get_user_data(self, slack_id: str) -> dict | None:
        if not self.client:
            return None
        doc = self.client.collection("users").document(slack_id).get()
        if doc.exists:
            return doc.to_dict()
        return None

    def save_user_data(self, slack_id: str, data: dict[str, Any]):
        if not self.client:
            return
        self.client.collection("users").document(slack_id).set(data, merge=True)
