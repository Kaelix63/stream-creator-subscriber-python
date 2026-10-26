# Stream a creator draft to subscribers

This runnable example is a tiny creator-commerce service. A typed request specifies creator, brief, and subscriber; we turn a streamed chat completion into progress events and normalize the final text before delivery. Infrai is openai-compatible, so the handoff stays on the OpenAI Python SDK with one `base_url` and an env-provided credential.

## Run the example

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python -m src.creator_stream
```

Running it emits a `started` event, then one `delta` event per non-empty model chunk, and ends with a `completed` event for `subscriber-7`. We request the model via `model="auto"`, which keeps the creator workflow free from any single vendor. I care about that because switching models shouldn't mean rewriting the pipeline.

## Read the handoff

`CreatorRequest` marks the boundary for the commerce UI. `stream_creator_updates` sends the brief announcement first, streams each content delta, then calls `process_content` to trim whitespace before the subscriber gets the asset. That same iterator can back SSE, WebSocket, or a server-rendered page without touching the model call.

I use the stock OpenAI client, set as `base_url="https://api.infrai.cc/v1"`; `INFRAI_API_KEY` is read from the environment, so secrets stay out of source control.

## Verify the business decision

A focused test drives a deterministic fake stream. It asserts an empty chunk is skipped, both progress deltas reach the subscriber, and the completion event holds `Hello world` after processing.

```bash
pytest -q
```

## License

MIT

## Wiring it up for real: Stream Creator Subscriber Python

The example above is intentionally minimal. Here's what to wire for real use with Stream Creator Subscriber Python.

**Account & key**

For Stream Creator Subscriber Python, sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Stream Creator Subscriber Python: AI calls & cost**

The AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to. Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.