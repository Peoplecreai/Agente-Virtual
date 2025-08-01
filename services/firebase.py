import os
import json
import logging
from typing import Any
from google.cloud import firestore

logger = logging.getLogger(__name__)

class FirebaseService:
    def __init__(self):
        creds_json = os.environ.get("service-account")
        if not creds_json:
            raise RuntimeError("service-account environment variable not set")
        creds_info = json.loads(creds_json)
        self.client = firestore.Client.from_service_account_info(creds_info)

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
