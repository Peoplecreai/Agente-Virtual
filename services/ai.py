import logging

logger = logging.getLogger(__name__)

try:
    from google import genai

    # The Client will read the GEMINI_API_KEY environment variable.
    client = genai.Client()
    GEMINI_AVAILABLE = True
except Exception as e:
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
