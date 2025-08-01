import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ.setdefault("GEMINI_API_KEY", "dummy")
import services.ai as ai_module
from services.ai import ConversationalAI

ai_module.GEMINI_AVAILABLE = False
ai_module.client = None

def test_ai_fallback():
    ai = ConversationalAI()
    response = ai.process_message("test", "Hola")
    assert response == "Lo siento, actualmente no puedo procesar tu solicitud."

if __name__ == "__main__":
    import sys
    sys.path.append('..')
