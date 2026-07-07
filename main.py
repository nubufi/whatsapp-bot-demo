import hashlib
import hmac
import json
import logging
import os
from typing import Any

from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, Header, HTTPException, Query, Request, Response, status
from fastapi.responses import PlainTextResponse

from engine import handle_message


load_dotenv()

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO").upper())
logger = logging.getLogger("whatsapp-webhook")

app = FastAPI(title="WhatsApp Business Webhook")


def get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Missing required environment variable: {name}",
        )
    return value


def verify_meta_signature(
    raw_body: bytes,
    x_hub_signature_256: str | None,
) -> None:
    app_secret = os.getenv("META_APP_SECRET")
    if not app_secret:
        return

    if not x_hub_signature_256:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing X-Hub-Signature-256 header",
        )

    try:
        algorithm, received_signature = x_hub_signature_256.split("=", 1)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid X-Hub-Signature-256 header",
        ) from exc

    if algorithm != "sha256":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unsupported webhook signature algorithm",
        )

    expected_signature = hmac.new(
        app_secret.encode("utf-8"),
        msg=raw_body,
        digestmod=hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(received_signature, expected_signature):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid webhook signature",
        )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


def enqueue_whatsapp_messages(payload: dict[str, Any], background_tasks: BackgroundTasks) -> int:
    message_count = 0

    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            phone_number_id = value.get("metadata", {}).get("phone_number_id")

            for message in value.get("messages", []):
                background_tasks.add_task(handle_message, message, phone_number_id)
                message_count += 1

    return message_count


@app.get("/webhook", response_class=PlainTextResponse)
@app.get("/webhook/whatsapp", response_class=PlainTextResponse)
async def verify_whatsapp_webhook(
    hub_mode: str = Query(alias="hub.mode"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
    hub_challenge: str = Query(alias="hub.challenge"),
) -> Response:
    verify_token = get_required_env("WHATSAPP_VERIFY_TOKEN")

    if hub_mode == "subscribe" and hub_verify_token == verify_token:
        return PlainTextResponse(content=hub_challenge, status_code=status.HTTP_200_OK)

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Webhook verification failed",
    )


@app.post("/webhook")
@app.post("/webhook/whatsapp")
async def receive_whatsapp_webhook(
    background_tasks: BackgroundTasks,
    request: Request,
    x_hub_signature_256: str | None = Header(default=None),
) -> dict[str, str]:
    raw_body = await request.body()
    verify_meta_signature(raw_body, x_hub_signature_256)

    try:
        payload: dict[str, Any] = json.loads(raw_body)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request body must be valid JSON",
        ) from exc

    logger.info("Received WhatsApp webhook: %s", json.dumps(payload, separators=(",", ":")))
    message_count = enqueue_whatsapp_messages(payload, background_tasks)
    logger.info("Queued %s WhatsApp message reply task(s)", message_count)

    return {"status": "EVENT_RECEIVED"}


def main() -> None:
    import uvicorn

    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("RELOAD", "false").lower() == "true",
    )


if __name__ == "__main__":
    main()
