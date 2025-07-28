import logging
import os

logger = logging.getLogger(__name__)

try:
    from google import genai

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    client = genai.Client(api_key=api_key) if api_key else None
    GEMINI_AVAILABLE = client is not None
except ImportError as e:
    logger.warning("Gemini not available: %s", e)
    client = None
    GEMINI_AVAILABLE = False

class ConversationalAI:
    def __init__(self):
        self.gemini_client = client if GEMINI_AVAILABLE else None
        self.model_name = "gemini-2.5-flash"
        if self.gemini_client:
            logger.info("Using Gemini 2.5 Flash model")

    def process_message(self, user: str, text: str) -> str:
        if self.gemini_client:
            try:
                response = self.gemini_client.models.generate_content(
                    model=self.model_name,
                    contents=text,
                )
                return response.text
            except Exception as e:
                logger.error("Gemini error: %s", e)
                self.gemini_client = None
        logger.error("No conversational AI available")
        return "Lo siento, actualmente no puedo procesar tu solicitud."
