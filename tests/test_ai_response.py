import ai_response


class FakeModel:
    def __init__(self) -> None:
        self.calls = []

    def invoke(self, messages):
        self.calls.append(messages)
        return type("Response", (), {"content": f"reply-{len(self.calls)}"})()


def test_generate_reply_includes_previous_turn(monkeypatch):
    fake_model = FakeModel()
    monkeypatch.setattr(ai_response, "get_chat_model", lambda: fake_model)
    monkeypatch.setenv("AI_HISTORY_MESSAGES", "12")
    ai_response._conversation_histories.clear()

    first_reply = ai_response.generate_reply("my name is numan", conversation_id="905551112233")
    second_reply = ai_response.generate_reply("what is my name", conversation_id="905551112233")

    assert first_reply == "reply-1"
    assert second_reply == "reply-2"
    second_call_contents = [message.content for message in fake_model.calls[1]]
    assert "my name is numan" in second_call_contents
    assert "reply-1" in second_call_contents
    assert second_call_contents[-1] == "what is my name"
