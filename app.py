import logging
import os
from flask import Flask, request
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler

from services.sheets import SheetService
from services.firebase import FirebaseService
from services.ai import ConversationalAI
from services.serpapi import SerpAPIService
from services.travel import TravelAssistant

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Slack app setup (do not modify request handling route)
bolt_app = App(token=os.environ.get("SLACK_BOT_TOKEN"),
               signing_secret=os.environ.get("SLACK_SIGNING_SECRET"))
handler = SlackRequestHandler(bolt_app)

sheet_service = SheetService()
firebase_service = FirebaseService()
ai_service = ConversationalAI()
serp_service = SerpAPIService()
assistant = TravelAssistant(sheet_service, firebase_service, ai_service, serp_service)

flask_app = Flask(__name__)


@bolt_app.event("message")
def handle_dm(event, say, ack):
    ack()
    if event.get("subtype") or event.get("bot_id"):
        return
    if event.get("channel_type") != "im":
        return
    slack_id = event.get("user")
    text = event.get("text", "")
    if not slack_id:
        return
    logger.info("DM from %s: %s", slack_id, text)
    response = assistant.handle_message(slack_id, text)
    say(response)


@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)


if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=8080)
