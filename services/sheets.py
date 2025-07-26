import os
import logging
import gspread
from google.oauth2.service_account import Credentials

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

class SheetService:
    def __init__(self):
        creds_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT")
        if not creds_json:
            logger.warning("GOOGLE_SERVICE_ACCOUNT not set; Sheets access disabled")
            self.client = None
        else:
            creds = Credentials.from_service_account_file(creds_json, scopes=SCOPES)
            self.client = gspread.authorize(creds)
        self.sheet_id = os.environ.get("GOOGLE_SHEET_ID")

    def get_user(self, slack_id: str) -> dict | None:
        if not self.client or not self.sheet_id:
            return None
        try:
            sheet = self.client.open_by_key(self.sheet_id).sheet1
            records = sheet.get_all_records()
            for row in records:
                if row.get("slack_id") == slack_id:
                    return row
        except Exception as e:
            logger.error("Error accessing Google Sheets: %s", e)
        return None
