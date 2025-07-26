import logging

try:
    from google.generativeai import GenerativeModel
    GEMINI_AVAILABLE = True
except Exception as e:
    logging.warning("Gemini not available: %s", e)
    GEMINI_AVAILABLE = False

# Placeholder for fallback open-source model (e.g., llama-cpp-python)
try:
    from llama_cpp import Llama
    LLAMA_AVAILABLE = True
except Exception as e:
    logging.warning("Llama model not available: %s", e)
    LLAMA_AVAILABLE = False

logger = logging.getLogger(__name__)

class ConversationalAI:
    def __init__(self):
        self.gemini_model = None
        if GEMINI_AVAILABLE:
            try:
                self.gemini_model = GenerativeModel("gemini-pro")
                logger.info("Using Gemini model")
            except Exception as e:
                logger.error("Failed to init Gemini: %s", e)
                self.gemini_model = None
        self.llama_model = None
        if not self.gemini_model and LLAMA_AVAILABLE:
            try:
                self.llama_model = Llama(model_path="model.bin")
                logger.info("Using Llama fallback model")
            except Exception as e:
                logger.error("Failed to load Llama: %s", e)
                self.llama_model = None

    def process_message(self, user: str, text: str) -> str:
        if self.gemini_model:
            try:
                response = self.gemini_model.generate_content(text)
                return response.text
            except Exception as e:
                logger.error("Gemini error: %s", e)
                self.gemini_model = None
        if self.llama_model:
            try:
                output = self.llama_model(text)
                return output["choices"][0]["text"]
            except Exception as e:
                logger.error("Llama error: %s", e)
                self.llama_model = None
        logger.error("No conversational AI available")
        return "Lo siento, actualmente no puedo procesar tu solicitud."
