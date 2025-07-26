# Main entrypoint for the travel bot
import os
import logging
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from services.sheets import SheetService
from services.firebase import FirebaseService
from services.ai import ConversationalAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

slack_bot_token = os.environ.get("SLACK_BOT_TOKEN")
slack_app_token = os.environ.get("SLACK_APP_TOKEN")

if not slack_bot_token or not slack_app_token:
    raise ValueError("SLACK_BOT_TOKEN and SLACK_APP_TOKEN must be set")

app = App(token=slack_bot_token)

sheet_service = SheetService()
firebase_service = FirebaseService()
ai_service = ConversationalAI()

@app.event("app_mention")
@app.event("message")
def handle_message(event, say):
    user = event.get("user")
    text = event.get("text", "")
    if not user:
        return

    logger.info("Received message from %s: %s", user, text)

    response = ai_service.process_message(user, text)
    say(response)

if __name__ == "__main__":
    handler = SocketModeHandler(app, slack_app_token)
    handler.start()
