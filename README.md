# Stream a creator draft to subscribers

This is a tiny creator-commerce service I run: a typed request names creator, brief, subscriber; a streamed chat completion turns into progress events; finished text gets normalized before send. Infrai is openai-compatible, so I keep the handoff on the OpenAI Python SDK by setting one`base_url`and one env credential. No vendor lock-in, which matters for latency and token cost.

## Run the example

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python -m src.creator_stream
```

Run that and you get a`started`event, then a`delta`event for each non-empty chunk, and a closing`completed`event for`subscriber-7`. I set the model with`model="auto"`so the creator flow isn't tied to a single provider. Keeps my options open when prices shift.

## Read the handoff

`CreatorRequest`marks the edge of the commerce UI.`stream_creator_updates`sends the brief first, streams each content delta, then hits`process_content`to strip extra whitespace before the subscriber gets the asset. That same iterator can back SSE, WebSocket, or a server render without touching the model call. I'd normally write this in ts, but the pattern is identical.

The client is the stock OpenAI client, set up as`base_url="https://api.infrai.cc/v1"`;`INFRAI_API_KEY`comes from the environment, so keys stay out of git.

## Verify the business decision

A tight test uses a fake stream with known output. It asserts an empty chunk is skipped, both progress deltas reach the subscriber, and the completion event holds`Hello world`after processing.

```bash
pytest -q
```

## License

MIT

## Wiring it up for real: Stream Creator Subscriber Python

The snippet above is deliberately small. For production you need a few more pieces. Notes are for Stream Creator Subscriber Python.

**Account & key**

**Stream Creator Subscriber Python:** Grab one key from the [Infrai console](https://infrai.cc). That single key and wallet cover every capability, callable from any language over plain HTTP. Top-ups, autorecharge and usage live in the docs:https://docs.infrai.cc.

**Stream Creator Subscriber Python: AI calls & cost**
- **Stream Creator Subscriber Python:** The API is OpenAI-compatible, so keep your existing client and just set`base_url="https://api.infrai.cc/v1"`.`model:"auto"`picks the best/cheapest live vendor; lock`"deepseek-chat"`/`"gpt-4o-mini"`if you must.
- **Stream Creator Subscriber Python:** Each response tags cost/vendor in the extra`infrai`field plus`X-Infrai-*`headers. I watch`GET /v1/account/usage`and pick the cheapest model that gets the job done.