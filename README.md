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
WHATSAPP_PHONE_NUMBER_ID=your-whatsapp-phone-number-id
META_APP_SECRET=
META_GRAPH_API_VERSION=v22.0
HOST=0.0.0.0
PORT=8000
RELOAD=false
```

`WHATSAPP_ACCESS_TOKEN` is required for the bot to send replies. You can use the temporary access token from the WhatsApp API Setup page while testing.

`WHATSAPP_PHONE_NUMBER_ID` is required for initiating conversations through the send-message endpoint.

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
- `POST /messages/template` sends a WhatsApp template message to start a conversation.
- `GET /webhook/whatsapp` handles Meta webhook verification using `hub.mode`, `hub.verify_token`, and `hub.challenge`.
- `POST /webhook/whatsapp` receives WhatsApp webhook JSON payloads, queues bot replies, and returns `{"status":"EVENT_RECEIVED"}`.
- `GET /webhook` and `POST /webhook` are aliases matching common tutorial examples.

Start a conversation by sending the configured WhatsApp template:

```bash
curl -X POST "http://127.0.0.1:8000/messages/template" \
  -H "Content-Type: application/json" \
  -d '{"phone_number":"905551112233","template_name":"your_approved_template","language":"en_US"}'
```

`template_name` must be an approved message template in your WhatsApp Business account. Meta's `hello_world` template only works with public test numbers.

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
