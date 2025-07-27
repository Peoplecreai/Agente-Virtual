import os
import json
import logging
import gspread
from google.oauth2.service_account import Credentials

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

class SheetService:
    def __init__(self):
        creds_json = os.environ.get("service-account")
        if not creds_json:
            raise RuntimeError("service-account environment variable not set")
        creds_info = json.loads(creds_json)
        creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
        self.client = gspread.authorize(creds)
        self.sheet_id = os.environ.get("GOOGLE_SHEET_ID")

    TEAM_ID = "T05NRU10WAW"

    def get_user(self, slack_id: str) -> dict | None:
        """Return the user record matching the organization Slack ID."""
        if not self.client or not self.sheet_id:
            return None
        try:
            sheet = self.client.open_by_key(self.sheet_id).sheet1
            records = sheet.get_all_records()

            combined = f"{self.TEAM_ID}-{slack_id}"

            for row in records:
                key = (
                    row.get("Slack ID")
                    or row.get("slack_id")
                    or row.get("Slack_Id")
                    or row.get("slack id")
                )
                if not key:
                    continue
                if key == combined:
                    return row
        except Exception as e:
            logger.error("Error accessing Google Sheets: %s", e)
        return None
