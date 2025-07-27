import sys, os, json
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ.setdefault("GEMINI_API_KEY", "dummy")

if "service-account" not in os.environ:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_key = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    os.environ["service-account"] = json.dumps(
        {
            "type": "service_account",
            "project_id": "dummy",
            "private_key_id": "dummy",
            "private_key": private_key,
            "client_email": "dummy@dummy.iam.gserviceaccount.com",
            "client_id": "dummy",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    )

from services.travel import TravelAssistant
from services.state import TravelState
import services.ai as ai_module
from services.ai import ConversationalAI
from services.serpapi import SerpAPIService


class DummySheetService:
    def get_user(self, slack_id: str):
        return None


class DummyFirebaseService:
    def get_user_data(self, slack_id: str):
        return None

    def save_user_data(self, slack_id: str, data: dict):
        pass

ai_module.GEMINI_AVAILABLE = False
ai_module.client = None


def test_travel_assistant_basic():
    ta = TravelAssistant(DummySheetService(), DummyFirebaseService(), ConversationalAI(), SerpAPIService())
    resp = ta.handle_message("U123", "Hola")
    assert isinstance(resp, str)


def test_parse_message_extended():
    ta = TravelAssistant(DummySheetService(), DummyFirebaseService(), ConversationalAI(), SerpAPIService())
    state = TravelState()
    ta._parse_message(state, "Quiero viajar de MEX a NYC el 2024-09-10, prefiero ventana y presupuesto $500")
    assert state.origin == "MEX"
    assert state.destination == "NYC"
    assert state.start_date == "2024-09-10"
    assert state.seat_pref == "ventana"
    assert state.budget == "500"
