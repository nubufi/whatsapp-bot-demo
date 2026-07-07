import os
from functools import lru_cache
from threading import Lock

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI


OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
SYSTEM_PROMPT = (
    "You are a helpful WhatsApp assistant. Reply conversationally, be concise, "
    "remember details the user has shared in this conversation, and avoid Markdown "
    "unless the user asks for formatting."
)
_conversation_histories: dict[str, list[BaseMessage]] = {}
_history_lock = Lock()


def get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"{name} is not configured")
    return value


@lru_cache(maxsize=1)
def get_chat_model() -> ChatOpenAI:
    default_headers = {}
    if referer := os.getenv("OPENROUTER_HTTP_REFERER"):
        default_headers["HTTP-Referer"] = referer
    if app_name := os.getenv("OPENROUTER_APP_NAME"):
        default_headers["X-Title"] = app_name

    return ChatOpenAI(
        api_key=get_required_env("OPENROUTER_API_KEY"),
        base_url=os.getenv("OPENROUTER_BASE_URL", OPENROUTER_BASE_URL),
        default_headers=default_headers or None,
        model=get_required_env("OPENROUTER_MODEL_ID"),
        temperature=float(os.getenv("OPENROUTER_TEMPERATURE", "0.7")),
    )


def get_history_limit() -> int:
    return int(os.getenv("AI_HISTORY_MESSAGES", "12"))


def get_conversation_messages(conversation_id: str, user_message: str) -> list[BaseMessage]:
    with _history_lock:
        history = list(_conversation_histories.get(conversation_id, []))

    return [SystemMessage(content=SYSTEM_PROMPT), *history, HumanMessage(content=user_message)]


def save_conversation_turn(conversation_id: str, user_message: str, ai_reply: str) -> None:
    with _history_lock:
        history = _conversation_histories.setdefault(conversation_id, [])
        history.extend([HumanMessage(content=user_message), AIMessage(content=ai_reply)])
        history_limit = get_history_limit()
        if history_limit > 0:
            del history[:-history_limit]


def generate_reply(user_message: str, conversation_id: str) -> str:
    response = get_chat_model().invoke(get_conversation_messages(conversation_id, user_message))

    content = response.content
    if isinstance(content, str):
        reply = content.strip()
    else:
        reply = str(content).strip()

    if reply:
        save_conversation_turn(conversation_id, user_message, reply)

    return reply
