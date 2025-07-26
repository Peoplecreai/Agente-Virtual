import logging
import os
import threading
from flask import Flask, request
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler

from services.sheets import SheetService
from services.firebase import FirebaseService
from services.ai import ConversationalAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

slack_bot_token = os.environ.get("SLACK_BOT_TOKEN")
slack_signing_secret = os.environ.get("SLACK_SIGNING_SECRET")

if not slack_bot_token or not slack_signing_secret:
    raise ValueError("SLACK_BOT_TOKEN and SLACK_SIGNING_SECRET must be set")

bolt_app = App(token=slack_bot_token, signing_secret=slack_signing_secret)
handler = SlackRequestHandler(bolt_app)

sheet_service = SheetService()
firebase_service = FirebaseService()
ai_service = ConversationalAI()


def process_and_respond(body, say):
    user = body.get("event", {}).get("user")
    text = body.get("event", {}).get("text", "")
    if not user:
        return
    logger.info("Received message from %s: %s", user, text)
    response = ai_service.process_message(user, text)
    say(response)


@bolt_app.event("message")
def handle_message(event, say, ack):
    ack()
    if event.get("subtype") or event.get("bot_id"):
        return
    if event.get("channel_type") != "im":
        return
    body = {"event": event}
    threading.Thread(target=process_and_respond, args=(body, say)).start()


flask_app = Flask(__name__)


@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)


if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=8080)
