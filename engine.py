import logging
from typing import Any

from ai_response import generate_reply
from send_message import send_message


logger = logging.getLogger("whatsapp-webhook")


def extract_message_text(message: dict[str, Any]) -> str | None:
    if message.get("type") != "text":
        return None

    text = message.get("text", {})
    body = text.get("body")
    if not isinstance(body, str):
        return None

    return body.strip() or None


def handle_message(message: dict[str, Any], phone_number_id: str | None) -> None:
    sender_id = message.get("from")
    if not sender_id:
        logger.warning("Skipping WhatsApp message without sender: %s", message)
        return

    if not phone_number_id:
        logger.warning("Skipping WhatsApp reply to %s: missing phone_number_id", sender_id)
        return

    message_text = extract_message_text(message)
    if not message_text:
        logger.info("Skipping non-text WhatsApp message from %s", sender_id)
        return

    try:
        reply = generate_reply(message_text, conversation_id=sender_id)
    except Exception as exc:
        logger.error("Failed to generate AI reply to %s: %s", sender_id, exc)
        return

    if not reply:
        logger.warning("Skipping empty AI reply to %s", sender_id)
        return

    send_message(sender_id, reply, phone_number_id)
