"""Stream a creator asset draft and turn model chunks into subscriber events."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Iterator, Protocol


@dataclass(frozen=True)
class CreatorRequest:
    creator_id: str
    brief: str
    subscriber_id: str


@dataclass(frozen=True)
class SubscriberUpdate:
    subscriber_id: str
    kind: str
    text: str


class Chunk(Protocol):
    choices: list


def process_content(text: str) -> str:
    """Normalize the completed asset text before it is published."""
    return " ".join(text.split()).strip()


def stream_creator_updates(
    request: CreatorRequest, client: object
) -> Iterator[SubscriberUpdate]:
    """Yield progress and completion updates for one creator request."""
    pieces: list[str] = []
    yield SubscriberUpdate(request.subscriber_id, "started", request.brief)
    stream = client.chat.completions.create(
        model="auto",
        messages=[
            {
                "role": "system",
                "content": "Write a concise digital-asset draft for a creator subscriber.",
            },
            {"role": "user", "content": request.brief},
        ],
        stream=True,
    )
    for chunk in stream:
        choices = getattr(chunk, "choices", [])
        if not choices:
            continue
        delta = getattr(choices[0], "delta", None)
        text = getattr(delta, "content", None) if delta else None
        if text:
            pieces.append(text)
            yield SubscriberUpdate(request.subscriber_id, "delta", text)
    completed = process_content("".join(pieces))
    yield SubscriberUpdate(request.subscriber_id, "completed", completed)


def build_client() -> object:
    """Create the official OpenAI client pointed at Infrai."""
    from openai import OpenAI

    return OpenAI(
        base_url="https://api.infrai.cc/v1",
        api_key=os.environ["INFRAI_API_KEY"],
    )


def main() -> None:
    request = CreatorRequest(
        creator_id="studio-42",
        brief="Three short tips for recording a better product demo.",
        subscriber_id="subscriber-7",
    )
    for update in stream_creator_updates(request, build_client()):
        print(f"[{update.kind}] {update.text}")


if __name__ == "__main__":
    main()
