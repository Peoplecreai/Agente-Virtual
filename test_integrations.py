import os
import json
import uuid
import requests
import datetime
import pytest

from slack_sdk import WebClient
import gspread
from google.oauth2.service_account import Credentials
from google.cloud import firestore
from google import genai

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

required_env = [
    "SLACK_BOT_TOKEN",
    "SERVICE_ACCOUNT",
    "GOOGLE_SHEET_ID",
    "SERPAPI_KEY",
    "GEMINI_API_KEY",
]

missing = [e for e in required_env if e not in os.environ]
if missing:
    pytest.skip("integration tests require credentials", allow_module_level=True)

def run_test(name, func):
    try:
        func()
        print(f"{name}: OK")
    except Exception as e:
        print(f"{name}: FAIL - {e}")

def test_slack():
    token = os.environ["SLACK_BOT_TOKEN"]
    channel = os.environ.get("SLACK_TEST_CHANNEL")
    if not channel:
        raise RuntimeError("SLACK_TEST_CHANNEL not set")
    client = WebClient(token=token)
    resp = client.chat_postMessage(channel=channel, text="Integration test")
    if not resp.get("ok"):
        raise RuntimeError(resp.get("error", "unknown error"))

def test_google_sheets():
    creds_info = json.loads(os.environ["SERVICE_ACCOUNT"])
    creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet_id = os.environ["GOOGLE_SHEET_ID"]
    sheet = client.open_by_key(sheet_id).sheet1
    _ = sheet.acell("A1").value

def test_firestore():
    creds_info = json.loads(os.environ["SERVICE_ACCOUNT"])
    client = firestore.Client.from_service_account_info(creds_info)
    doc_ref = client.collection("test").document(str(uuid.uuid4()))
    doc_ref.set({"value": "ok"})
    doc = doc_ref.get()
    if not doc.exists or doc.to_dict().get("value") != "ok":
        raise RuntimeError("Firestore read failed")
    doc_ref.delete()

def test_serpapi():
    api_key = os.environ["SERPAPI_KEY"]
    future_departure = (datetime.date.today() + datetime.timedelta(days=2)).strftime("%Y-%m-%d")
    future_return = (datetime.date.today() + datetime.timedelta(days=7)).strftime("%Y-%m-%d")
    params = {
        "api_key": api_key,
        "engine": "google_flights",
        "hl": "en",
        "gl": "mx",
        "departure_id": "MEX",
        "arrival_id": "SFO",
        "outbound_date": future_departure,
        "return_date": future_return,
        "currency": "USD",
        "travel_class": "1"
    }
    resp = requests.get("https://serpapi.com/search.json", params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if "error" in data:
        raise RuntimeError(data["error"])

def test_gemini():
    api_key = os.environ["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(model="gemini-2.5-flash", contents="Hola")
    if not getattr(response, "text", ""):
        raise RuntimeError("Empty response")

if __name__ == "__main__":
    run_test("Slack", test_slack)
    run_test("Google Sheets", test_google_sheets)
    run_test("Firestore", test_firestore)
    run_test("SerpApi", test_serpapi)
    run_test("Gemini", test_gemini)
