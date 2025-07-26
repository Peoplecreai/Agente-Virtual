import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from services.ai import ConversationalAI

def test_ai_fallback():
    ai = ConversationalAI()
    response = ai.process_message("test", "Hola")
    assert isinstance(response, str)

if __name__ == "__main__":
    import sys
    sys.path.append('..')
