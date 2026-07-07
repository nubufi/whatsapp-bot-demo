# Repository Guidelines

## Project Structure & Module Organization

This is a small FastAPI service for WhatsApp Business webhooks. Source files live at the repository root:

- `main.py` defines the FastAPI app, webhook verification, signature validation, and HTTP endpoints.
- `engine.py` contains message-handling logic invoked from background tasks.
- `send_message.py` wraps WhatsApp Cloud API calls for text and template messages.
- `README.md` documents setup, environment variables, and endpoint behavior.
- `pyproject.toml` and `uv.lock` define the Python 3.13 dependency set.

There is no dedicated `tests/` directory yet. Add one when introducing test coverage, and mirror module names, for example `tests/test_main.py`.

## Build, Test, and Development Commands

- `uv sync` installs the locked dependency environment.
- `make run` starts the service with `uv run python main.py`.
- `make run_dev` starts the service with `RELOAD=true` for local reload behavior.
- `uv run python main.py` is the direct entry point if Make is unavailable.

The default app listens on `0.0.0.0:8000`. For webhook testing, expose this port through an HTTPS tunnel and configure Meta to call `/webhook/whatsapp`.

## Coding Style & Naming Conventions

Use Python 3.13 syntax and type hints, matching the existing code. Keep modules focused: HTTP concerns belong in `main.py`, WhatsApp API transport in `send_message.py`, and bot behavior in `engine.py`. Use 4-space indentation, `snake_case` for functions and variables, and clear Pydantic model names such as `SendTemplateMessageRequest`.

Prefer standard library utilities unless a dependency is already present or clearly justified. Keep logging under the `whatsapp-webhook` logger.

## Testing Guidelines

No test framework is currently configured. When adding tests, prefer `pytest` with FastAPI `TestClient` for endpoint behavior and monkeypatched environment variables for token and signature cases. Cover webhook verification, invalid JSON, signature rejection, and template-send error handling. Run tests with `uv run pytest` once `pytest` is added to the project dependencies.

## Commit & Pull Request Guidelines

Recent commits use short imperative subjects, such as `Add WhatsApp webhook bot` and `Add template message endpoint`. Keep that style: one focused change per commit, with a concise subject.

Pull requests should include a brief summary, any required environment variable changes, test results, and sample request/response details for endpoint changes. Link related issues when available and include screenshots only when documenting external dashboard configuration.

## Security & Configuration Tips

Do not commit `.env` files or Meta access tokens. Use `META_APP_SECRET` in production so incoming webhooks require `X-Hub-Signature-256`. Keep `WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`, and template names environment-specific.
