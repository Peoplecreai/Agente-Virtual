import logging
from typing import Any, List

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
                self.firebase.save_user_data(slack_id, data)
        return data

    def _save_history(self, slack_id: str, history: List[dict]):
        self.firebase.save_user_data(slack_id, {"history": history})

    def build_prompt(self, user_data: dict, history: List[dict], message: str) -> str:
        policy = (
            "Política de Viajes Creai:\n"
            "Reservaciones 7 días antes, info completa obligatoria.\n"
            "Vuelos: Económica, carry-on incluido, asiento seleccionable según política, premier solo con autorización especial.\n"
            "Hospedaje: Límite por seniority y región. Hoteles seguros y cerca del venue. Habitación compartida solo si el usuario acepta.\n"
            "Viáticos: Por país, justificación o anticipo según política.\n"
            "Autorizaciones: Finanzas autoriza, Presidencia para excepciones.\n"
            "No cubierto: fechas fuera del evento, room service, minibar, spa, gimnasio, transporte ajeno, etc.\n"
            "Casos especiales: Solo con autorización de Presidencia."
        )
        context = "\n".join(
            f"Usuario: {h['user']}" if 'user' in h else f"Bot: {h['bot']}" for h in history
        )
        prompt = f"{policy}\n{context}\nUsuario: {message}\nBot:".strip()
        return prompt

    def handle_message(self, slack_id: str, text: str) -> str:
        user_data = self._load_user(slack_id)
        history = user_data.get("history", [])
        history.append({"user": text})
        prompt = self.build_prompt(user_data, history, text)
        response = self.ai.process_message(slack_id, prompt)
        history.append({"bot": response})
        self._save_history(slack_id, history[-20:])  # keep last 20 messages
        return response

    # Example methods for fetching travel data
    def find_flights(self, origin: str, destination: str, date: str) -> List[dict]:
        return self.serpapi.search_flights(origin, destination, date)

    def find_hotels(self, city: str, check_in: str, check_out: str) -> List[dict]:
        return self.serpapi.search_hotels(city, check_in, check_out)
