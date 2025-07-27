import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services.travel import TravelAssistant
from services.state import TravelState
from services.sheets import SheetService
from services.firebase import FirebaseService
from services.ai import ConversationalAI
from services.serpapi import SerpAPIService


def test_travel_assistant_basic():
    ta = TravelAssistant(SheetService(), FirebaseService(), ConversationalAI(), SerpAPIService())
    resp = ta.handle_message("U123", "Hola")
    assert isinstance(resp, str)


def test_parse_message_extended():
    ta = TravelAssistant(SheetService(), FirebaseService(), ConversationalAI(), SerpAPIService())
    state = TravelState()
    ta._parse_message(state, "Quiero viajar de MEX a NYC el 2024-09-10, prefiero ventana y presupuesto $500")
    assert state.origin == "MEX"
    assert state.destination == "NYC"
    assert state.start_date == "2024-09-10"
    assert state.seat_pref == "ventana"
    assert state.budget == "500"
