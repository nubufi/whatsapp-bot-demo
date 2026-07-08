from typing import Any

from fastapi.testclient import TestClient

import main
from send_message import send_template_message


def test_send_template_message_includes_body_variables(monkeypatch) -> None:
    captured_payload: dict[str, Any] = {}

    def fake_post_whatsapp_message(
        phone_number_id: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        captured_payload["phone_number_id"] = phone_number_id
        captured_payload["payload"] = payload
        return {"messages": [{"id": "wamid.test"}]}

    monkeypatch.setattr("send_message.post_whatsapp_message", fake_post_whatsapp_message)

    response = send_template_message(
        to="905551112233",
        language="en_US",
        phone_number_id="12345",
        template_name="appointment_reminder",
        template_variables=["Ada", "Friday", 42],
    )

    assert response == {"messages": [{"id": "wamid.test"}]}
    assert captured_payload == {
        "phone_number_id": "12345",
        "payload": {
            "messaging_product": "whatsapp",
            "to": "905551112233",
            "type": "template",
            "template": {
                "name": "appointment_reminder",
                "language": {"code": "en_US"},
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": "Ada"},
                            {"type": "text", "text": "Friday"},
                            {"type": "text", "text": "42"},
                        ],
                    }
                ],
            },
        },
    }


def test_send_template_message_includes_named_body_variables(monkeypatch) -> None:
    captured_payload: dict[str, Any] = {}

    def fake_post_whatsapp_message(
        phone_number_id: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        captured_payload["phone_number_id"] = phone_number_id
        captured_payload["payload"] = payload
        return {"messages": [{"id": "wamid.test"}]}

    monkeypatch.setattr("send_message.post_whatsapp_message", fake_post_whatsapp_message)

    response = send_template_message(
        to="905551112233",
        language="en",
        phone_number_id="12345",
        template_name="welcome",
        template_variables={"name": "Numan"},
    )

    assert response == {"messages": [{"id": "wamid.test"}]}
    assert captured_payload["payload"]["template"]["components"] == [
        {
            "type": "body",
            "parameters": [
                {"type": "text", "parameter_name": "name", "text": "Numan"},
            ],
        }
    ]


def test_template_endpoint_passes_template_variables(monkeypatch) -> None:
    captured_call: dict[str, Any] = {}

    def fake_send_template_message(**kwargs) -> dict[str, Any]:
        captured_call.update(kwargs)
        return {"messages": [{"id": "wamid.endpoint"}]}

    monkeypatch.setenv("WHATSAPP_PHONE_NUMBER_ID", "12345")
    monkeypatch.setattr(main, "send_template_message", fake_send_template_message)

    client = TestClient(main.app)
    response = client.post(
        "/messages/template",
        json={
            "phone_number": "905551112233",
            "template_name": "appointment_reminder",
            "language": "en_US",
            "template_variables": ["Ada", "Friday", 42],
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "status": "sent",
        "response": {"messages": [{"id": "wamid.endpoint"}]},
    }
    assert captured_call == {
        "to": "905551112233",
        "language": "en_US",
        "phone_number_id": "12345",
        "template_name": "appointment_reminder",
        "template_variables": ["Ada", "Friday", 42],
    }


def test_template_endpoint_accepts_named_template_variables(monkeypatch) -> None:
    captured_call: dict[str, Any] = {}

    def fake_send_template_message(**kwargs) -> dict[str, Any]:
        captured_call.update(kwargs)
        return {"messages": [{"id": "wamid.endpoint"}]}

    monkeypatch.setenv("WHATSAPP_PHONE_NUMBER_ID", "12345")
    monkeypatch.setattr(main, "send_template_message", fake_send_template_message)

    client = TestClient(main.app)
    response = client.post(
        "/messages/template",
        json={
            "phone_number": "905551112233",
            "template_name": "welcome",
            "language": "en",
            "template_variables": {"name": "Numan"},
        },
    )

    assert response.status_code == 200
    assert captured_call["template_variables"] == {"name": "Numan"}
