"""Slack entrypoint for the corporate travel assistant."""

import hashlib
import hmac
import logging
import os
from threading import Thread

from flask import Flask, jsonify, request
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from services.sheets import SheetService
from services.firebase import FirebaseService
from services.ai import ConversationalAI
from services.serpapi import SerpAPIService
from services.travel import TravelAssistant

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Slack client setup
slack_token = os.environ.get("SLACK_BOT_TOKEN")
if not slack_token:
    raise RuntimeError("SLACK_BOT_TOKEN environment variable not set")

client = WebClient(token=slack_token)

BOT_USER_ID = os.environ.get("BOT_USER_ID")
if not BOT_USER_ID:
    try:
        auth_info = client.auth_test()
        BOT_USER_ID = auth_info.get("user_id")
    except SlackApiError as e:
        logger.error("Failed to fetch bot user ID: %s", e.response["error"])
        BOT_USER_ID = None

signing_secret = os.environ.get("SLACK_SIGNING_SECRET")

sheet_service = SheetService()
firebase_service = FirebaseService()
ai_service = ConversationalAI()
serp_service = SerpAPIService()
assistant = TravelAssistant(sheet_service, firebase_service, ai_service, serp_service)

flask_app = Flask(__name__)

processed_ids: set[str] = set()
sent_ts: set[str] = set()


def _verify_request(req: request) -> bool:
    """Validate Slack signature."""
    if not signing_secret:
        return True
    timestamp = req.headers.get("X-Slack-Request-Timestamp", "")
    body = req.get_data(as_text=True)
    sig_basestring = f"v0:{timestamp}:{body}"
    my_sig = "v0=" + hmac.new(signing_secret.encode(), sig_basestring.encode(), hashlib.sha256).hexdigest()
    slack_sig = req.headers.get("X-Slack-Signature", "")
    return hmac.compare_digest(my_sig, slack_sig)


def handle_event(data: dict) -> None:
    event = data.get("event", {})
    event_type = event.get("type")
    event_ts = event.get("ts")
    user = event.get("user")
    bot_id = event.get("bot_id")
    subtype = event.get("subtype")
    thread_ts = event.get("thread_ts") or event_ts

    if (event_ts in sent_ts) or (user == BOT_USER_ID) or bot_id or subtype == "bot_message":
        return

    if event_type == "assistant_thread_started":
        try:
            welcome = "Hola \U0001F44B Soy tu asistente de viajes. Escr\u00edbeme cualquier pregunta."
            client.chat_postMessage(channel=event["channel"], text=welcome, mrkdwn=True, thread_ts=thread_ts)
        except SlackApiError as e:
            logger.error("Error posting welcome message: %s", e.response["error"])
        return

    if event_type == "message" and subtype is None:
        if event.get("channel", "").startswith("D") or event.get("channel_type") in {"im", "app_home"}:
            try:
                textout = assistant.handle_message(user, event.get("text", ""))
                resp = client.chat_postMessage(channel=event["channel"], text=textout, mrkdwn=True, thread_ts=thread_ts)
                sent_ts.add(resp.get("ts"))
            except SlackApiError as e:
                logger.error("Error posting message: %s", e.response["error"])
        return

    if event_type == "app_mention" and event.get("client_msg_id") not in processed_ids:
        if user == BOT_USER_ID:
            return
        try:
            textout = assistant.handle_message(user, event.get("text", ""))
            resp = client.chat_postMessage(channel=event["channel"], text=textout, mrkdwn=True, thread_ts=thread_ts)
            sent_ts.add(resp.get("ts"))
            processed_ids.add(event.get("client_msg_id"))
        except SlackApiError as e:
            logger.error("Error posting message: %s", e.response["error"])
        return


def handle_event_async(data: dict) -> None:
    Thread(target=handle_event, args=(data,), daemon=True).start()


@flask_app.route("/", methods=["POST"])
def slack_events() -> tuple[str, int] | tuple[dict, int]:
    if not _verify_request(request):
        return "", 403
    data = request.get_json(silent=True) or {}
    if data.get("type") == "url_verification":
        return jsonify({"challenge": data.get("challenge")}), 200
    if data.get("event"):
        handle_event_async(data)
    return "", 200


if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=8080)
