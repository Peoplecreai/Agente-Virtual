import logging
import os

logger = logging.getLogger(__name__)

try:
    from google import genai
    from google.genai.errors import APIError
    # The Client will read the GEMINI_API_KEY environment variable.
    client = genai.Client()
    GEMINI_AVAILABLE = True
except Exception as e:
    logger.warning("Gemini not available: %s", e)
    client = None
    GEMINI_AVAILABLE = False

try:
    from llama_cpp import Llama
    LLAMA_AVAILABLE = True
except Exception as e:
    logger.warning("Llama model not available: %s", e)
    LLAMA_AVAILABLE = False

class ConversationalAI:
    def __init__(self):
        self.gemini_client = None
        self.model_name = "gemini-2.5-flash"
        if GEMINI_AVAILABLE:
            self.gemini_client = client
            logger.info("Using Gemini 2.5 Flash model")
        self.llama_model = None
        if not self.gemini_client and LLAMA_AVAILABLE and os.environ.get("LLAMA_MODEL_PATH"):
            try:
                self.llama_model = Llama(model_path=os.environ["LLAMA_MODEL_PATH"])
                logger.info("Using Llama fallback model")
            except Exception as e:
                logger.error("Failed to load Llama: %s", e)
                self.llama_model = None

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
        if self.llama_model:
            try:
                output = self.llama_model(text)
                return output["choices"][0]["text"]
            except Exception as e:
                logger.error("Llama error: %s", e)
                self.llama_model = None
        logger.error("No conversational AI available")
        return "Lo siento, actualmente no puedo procesar tu solicitud."
