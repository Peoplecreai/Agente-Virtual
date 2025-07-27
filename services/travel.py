import logging
import re
from typing import Any, List

from .state import TravelState

from .firebase import FirebaseService
from .sheets import SheetService
from .ai import ConversationalAI
from .serpapi import SerpAPIService

logger = logging.getLogger(__name__)


class TravelAssistant:
    """Main orchestrator for travel conversations."""

    def __init__(
        self,
        sheets: SheetService,
        firebase: FirebaseService,
        ai: ConversationalAI,
        serpapi: SerpAPIService,
    ) -> None:
        self.sheets = sheets
        self.firebase = firebase
        self.ai = ai
        self.serpapi = serpapi

    def _load_user(self, slack_id: str) -> dict:
        data = self.firebase.get_user_data(slack_id) or {}
        if not data:
            sheet_user = self.sheets.get_user(slack_id)
            if sheet_user:
                data.update(sheet_user)
        if "history" not in data:
            data["history"] = []
        if "state" not in data:
            data["state"] = {}
        self.firebase.save_user_data(slack_id, data)
        return data

    def _save_history(self, slack_id: str, history: List[dict]):
        self.firebase.save_user_data(slack_id, {"history": history})

    def _load_state(self, user_data: dict) -> TravelState:
        return TravelState.from_dict(user_data.get("state", {}))

    def _save_state(self, slack_id: str, state: TravelState):
        self.firebase.save_user_data(slack_id, {"state": state.to_dict()})

    def _parse_message(self, state: TravelState, text: str):
        """Extract basic travel information from the user's message."""
        if not state.origin or not state.destination:
            codes = re.findall(r"\b[A-Z]{3}\b", text.upper())
            if codes:
                if not state.origin and len(codes) >= 1:
                    state.origin = codes[0]
                if not state.destination and len(codes) >= 2:
                    state.destination = codes[1]
        if not state.start_date or not state.end_date:
            dates = re.findall(r"\d{4}-\d{2}-\d{2}", text)
            if dates:
                if not state.start_date and len(dates) >= 1:
                    state.start_date = dates[0]
                if not state.end_date and len(dates) >= 2:
                    state.end_date = dates[1]
        if not state.seat_pref:
            if "ventana" in text.lower():
                state.seat_pref = "ventana"
            elif "pasillo" in text.lower():
                state.seat_pref = "pasillo"
        if not state.share_room and "compartir" in text.lower():
            state.share_room = True
        if "no compartir" in text.lower():
            state.share_room = False
        if not state.passport and "pasaporte" in text.lower():
            state.passport = "si" in text.lower()
        if not state.visa and "visa" in text.lower():
            state.visa = "si" in text.lower()
        if not state.budget:
            m = re.search(r"(?:\$|presupuesto\s*)(\d+)", text.lower())
            if m:
                state.budget = m.group(1)

    def build_prompt(self, user_data: dict, state: TravelState, history: List[dict], message: str) -> str:
        policy = (
            "Eres un asistente de viajes corporativos integrado con Slack y Google Sheets.\n"
            "Obtén nombre completo, fecha de nacimiento, seniority y departamento automáticamente con el Slack ID.\n"
            "Solo pregunta por origen, destino, fechas de salida y regreso, motivo o venue y preferencias opcionales.\n"
            "Nunca menciones políticas ni pidas datos personales antes de elegir opciones.\n"
            "Muestra únicamente vuelos y hoteles dentro del presupuesto; incluye carry-on en todas las búsquedas de vuelos.\n"
            "Cuando el usuario confirme vuelo y hotel, solicita: nombre completo y fecha de nacimiento (prellenados), número de pasaporte y visa si aplica.\n"
            "Confirma que los datos sean correctos y envía la solicitud a Finanzas.\n"
            "Permite correcciones en cualquier momento y evita repeticiones innecesarias."
        )
        context = "\n".join(
            f"Usuario: {h['user']}" if 'user' in h else f"Bot: {h['bot']}" for h in history[-5:]
        )
        state_lines = "\n".join(f"{k}: {v}" for k, v in state.to_dict().items()) or "ninguno"
        required_fields = ["origin", "destination", "start_date", "end_date"]
        missing = [f for f in required_fields if not getattr(state, f)]
        missing_text = ", ".join(missing) if missing else "ninguno"
        prompt = (
            f"{policy}\n"
            f"Datos recopilados:\n{state_lines}\n"
            f"Faltantes: {missing_text}\n"
            f"{context}\n"
            f"Usuario: {message}\nBot:"
        )
        return prompt.strip()

    def handle_message(self, slack_id: str, text: str) -> str:
        user_data = self._load_user(slack_id)
        history = user_data.get("history", [])
        state = self._load_state(user_data)
        history.append({"user": text})

        self._parse_message(state, text)

        prompt = self.build_prompt(user_data, state, history, text)
        response = self.ai.process_message(slack_id, prompt)

        history.append({"bot": response})
        self._save_history(slack_id, history[-20:])
        self._save_state(slack_id, state)

        return response

    # Example methods for fetching travel data
    def find_flights(self, origin: str, destination: str, date: str) -> List[dict]:
        return self.serpapi.search_flights(origin, destination, date)

    def find_hotels(self, city: str, check_in: str, check_out: str) -> List[dict]:
        return self.serpapi.search_hotels(city, check_in, check_out)
