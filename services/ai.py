import logging
import os

try:
    from google import genai
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        GEMINI_AVAILABLE = True
    else:
        GEMINI_AVAILABLE = False
except Exception as e:
    logging.warning("Gemini not available: %s", e)
    GEMINI_AVAILABLE = False

try:
    from llama_cpp import Llama
    LLAMA_AVAILABLE = True
except Exception as e:
    logging.warning("Llama model not available: %s", e)
    LLAMA_AVAILABLE = False

logger = logging.getLogger(__name__)


class ConversationalAI:
    def __init__(self):
        self.client = genai.Client() if GEMINI_AVAILABLE else None
        self.llama_model = None
        if not self.client and LLAMA_AVAILABLE and os.environ.get("LLAMA_MODEL_PATH"):
            try:
                self.llama_model = Llama(model_path=os.environ["LLAMA_MODEL_PATH"])
                logger.info("Using Llama fallback model")
            except Exception as e:
                logger.error("Failed to load Llama: %s", e)
                self.llama_model = None

    def process_message(self, user: str, text: str) -> str:
        if self.client:
            try:
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=text,
                )
                return response.text
            except Exception as e:
                logger.error("Gemini error: %s", e)
                self.client = None
        if self.llama_model:
            try:
                output = self.llama_model(text)
                return output["choices"][0]["text"]
            except Exception as e:
                logger.error("Llama error: %s", e)
                self.llama_model = None
        logger.error("No conversational AI available")
        return "Lo siento, actualmente no puedo procesar tu solicitud."
