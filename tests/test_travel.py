import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services.travel import TravelAssistant
from services.sheets import SheetService
from services.firebase import FirebaseService
from services.ai import ConversationalAI
from services.serpapi import SerpAPIService


def test_travel_assistant_basic():
    ta = TravelAssistant(SheetService(), FirebaseService(), ConversationalAI(), SerpAPIService())
    resp = ta.handle_message("U123", "Hola")
    assert isinstance(resp, str)
