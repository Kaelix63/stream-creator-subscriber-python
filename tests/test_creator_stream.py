from types import SimpleNamespace

from src.creator_stream import CreatorRequest, stream_creator_updates


class FakeCompletions:
    def create(self, **kwargs):
        assert kwargs["model"] == "auto"
        assert kwargs["stream"] is True
        return iter(
            [
                SimpleNamespace(choices=[]),
                SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content=" Hello"))]),
                SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content="  world "))]),
            ]
        )


class FakeClient:
    chat = SimpleNamespace(completions=FakeCompletions())


def test_stream_publishes_progress_and_normalized_completion():
    request = CreatorRequest("creator-1", "Draft a welcome note", "subscriber-1")
    updates = list(stream_creator_updates(request, FakeClient()))

    assert [item.kind for item in updates] == ["started", "delta", "delta", "completed"]
    assert updates[-1].text == "Hello world"
    assert updates[-1].subscriber_id == "subscriber-1"
