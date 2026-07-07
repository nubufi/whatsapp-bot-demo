import json
import logging
import os
import urllib.error
import urllib.request
from typing import Any


logger = logging.getLogger("whatsapp-webhook")


def get_access_token() -> str | None:
    return os.getenv("WHATSAPP_ACCESS_TOKEN") or os.getenv("ACCESS_TOKEN")


def post_whatsapp_message(phone_number_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    access_token = get_access_token()
    if not access_token:
        raise RuntimeError("WHATSAPP_ACCESS_TOKEN is not configured")

    graph_api_version = os.getenv("META_GRAPH_API_VERSION", "v22.0")
    url = f"https://graph.facebook.com/{graph_api_version}/{phone_number_id}/messages"
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            response_body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8")
        raise RuntimeError(f"WhatsApp API returned HTTP {exc.code}: {error_body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Failed to call WhatsApp API: {exc.reason}") from exc

    if not response_body:
        return {}

    return json.loads(response_body)


def send_message(to: str, message: str, phone_number_id: str) -> None:
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": message},
    }

    try:
        response_body = post_whatsapp_message(phone_number_id, payload)
    except RuntimeError as exc:
        logger.error("Failed to send WhatsApp message to %s: %s", to, exc)
        return

    logger.info("Sent WhatsApp message to %s: %s", to, response_body)


def send_template_message(
    to: str,
    language: str,
    phone_number_id: str,
    template_name: str = "hello_world",
) -> dict[str, Any]:
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": language},
        },
    }

    return post_whatsapp_message(phone_number_id, payload)
