import json
import logging
import os
import urllib.error
import urllib.request


logger = logging.getLogger("whatsapp-webhook")


def get_access_token() -> str | None:
    return os.getenv("WHATSAPP_ACCESS_TOKEN") or os.getenv("ACCESS_TOKEN")


def send_message(to: str, message: str, phone_number_id: str) -> None:
    access_token = get_access_token()
    if not access_token:
        logger.error("Cannot send WhatsApp message: ACCESS_TOKEN is not configured")
        return

    graph_api_version = os.getenv("META_GRAPH_API_VERSION", "v22.0")
    url = f"https://graph.facebook.com/{graph_api_version}/{phone_number_id}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": message},
    }
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
        logger.error(
            "Failed to send WhatsApp message to %s: HTTP %s %s",
            to,
            exc.code,
            error_body,
        )
        return
    except urllib.error.URLError as exc:
        logger.error("Failed to send WhatsApp message to %s: %s", to, exc.reason)
        return

    logger.info("Sent WhatsApp message to %s: %s", to, response_body)
