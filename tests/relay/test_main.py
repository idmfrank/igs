import asyncio
import json
from pathlib import Path
import sys

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from apps.relay.main import (  # noqa: E402
    EVENT_HISTORY,
    SUBSCRIBERS,
    PublishPayload,
    register_subscriber,
    stream_topic_events,
    publish,
)


@pytest.fixture(autouse=True)
def clear_state():
    EVENT_HISTORY.clear()
    SUBSCRIBERS.clear()


async def _read_next_event(stream):
    event = await asyncio.wait_for(stream.__anext__(), timeout=1.0)
    assert event["event"] == "message"
    return json.loads(event["data"])


def test_publish_replays_history():
    async def scenario():
        topic = "history"
        payload = {"value": 1}

        await publish(PublishPayload(topic=topic, payload=payload))

        queue: asyncio.Queue[str] = asyncio.Queue()
        await register_subscriber(topic, queue)
        stream = stream_topic_events(topic, queue)

        event = await _read_next_event(stream)
        assert event["topic"] == topic
        assert event["payload"] == payload

        await stream.aclose()
        await asyncio.sleep(0)
        assert topic not in SUBSCRIBERS or not SUBSCRIBERS[topic]

    asyncio.run(scenario())


def test_subscribe_receives_new_events():
    async def scenario():
        topic = "live"
        payload = {"value": "fresh"}

        queue: asyncio.Queue[str] = asyncio.Queue()
        await register_subscriber(topic, queue)
        stream = stream_topic_events(topic, queue)

        pending = asyncio.create_task(_read_next_event(stream))

        await publish(PublishPayload(topic=topic, payload=payload))

        event = await pending
        assert event["topic"] == topic
        assert event["payload"] == payload

        await stream.aclose()
        await asyncio.sleep(0)
        assert topic not in SUBSCRIBERS or not SUBSCRIBERS[topic]

    asyncio.run(scenario())
