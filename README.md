# WhatsApp Business Webhook

FastAPI webhook endpoint for WhatsApp Business Platform callbacks.

## Setup

Install dependencies with uv:

```bash
uv sync
```

Set the verification token. This must match the "Verify token" value you enter in the Meta app dashboard.

```bash
cp .env.example .env
```

Then edit `.env`:

```env
WHATSAPP_VERIFY_TOKEN=your-verify-token
WHATSAPP_ACCESS_TOKEN=your-meta-whatsapp-cloud-api-token
META_APP_SECRET=
META_GRAPH_API_VERSION=v22.0
HOST=0.0.0.0
PORT=8000
RELOAD=false
```

`WHATSAPP_ACCESS_TOKEN` is required for the bot to send replies. You can use the temporary access token from the WhatsApp API Setup page while testing.

`META_APP_SECRET` is optional but recommended for production. When set, incoming POST requests must include a valid `X-Hub-Signature-256` header.

Run the server:

```bash
make run
```

For local development with reload:

```bash
make run_dev
```

The default server listens on `http://0.0.0.0:8000`.

## Endpoints

- `GET /health` returns a basic health check.
- `GET /webhook/whatsapp` handles Meta webhook verification using `hub.mode`, `hub.verify_token`, and `hub.challenge`.
- `POST /webhook/whatsapp` receives WhatsApp webhook JSON payloads, queues bot replies, and returns `{"status":"EVENT_RECEIVED"}`.
- `GET /webhook` and `POST /webhook` are aliases matching common tutorial examples.

When a WhatsApp message webhook includes `metadata.phone_number_id` and `messages[].from`, the bot sends this reply through the WhatsApp Cloud API:

```text
Hey, your bot is up!
```

Use this as the callback URL in Meta after exposing the server over HTTPS:

```text
https://your-domain.example/webhook/whatsapp
```

If you want to follow tutorials that use `/webhook`, this callback URL also works:

```text
https://your-domain.example/webhook
```

For local testing, expose port `8000` with a tunnel such as ngrok or Cloudflare Tunnel and use the HTTPS tunnel URL.
