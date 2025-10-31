
import asyncio
import json
import time
import uuid
from collections import defaultdict, deque
from typing import Any, AsyncIterator, Deque, Dict, List, Set

from fastapi import FastAPI
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

app = FastAPI(title="Relay")

MAX_EVENTS_PER_TOPIC = 50

EVENT_HISTORY: Dict[str, Deque[Dict[str, Any]]] = defaultdict(deque)
SUBSCRIBERS: Dict[str, Set[asyncio.Queue[str]]] = defaultdict(set)

history_lock = asyncio.Lock()
subscriber_lock = asyncio.Lock()


class PublishPayload(BaseModel):
    topic: str
    payload: Dict[str, Any]


@app.post("/publish")
async def publish(msg: PublishPayload):
    evt = {
        "id": str(uuid.uuid4()),
        "ts": time.time(),
        "topic": msg.topic,
        "payload": msg.payload,
    }

    async with history_lock:
        history = EVENT_HISTORY[msg.topic]
        history.append(evt)
        while len(history) > MAX_EVENTS_PER_TOPIC:
            history.popleft()

    data = json.dumps(evt)

    async with subscriber_lock:
        queues: List[asyncio.Queue[str]] = list(SUBSCRIBERS.get(msg.topic, set()))

    for queue in queues:
        await queue.put(data)

    return {"status": "ok", "event_id": evt["id"]}


async def snapshot_topic_history(topic: str) -> List[Dict[str, Any]]:
    async with history_lock:
        return list(EVENT_HISTORY.get(topic, []))


async def register_subscriber(topic: str, queue: asyncio.Queue[str]) -> None:
    async with subscriber_lock:
        SUBSCRIBERS[topic].add(queue)


async def unregister_subscriber(topic: str, queue: asyncio.Queue[str]) -> None:
    async with subscriber_lock:
        topic_subscribers = SUBSCRIBERS.get(topic)
        if topic_subscribers and queue in topic_subscribers:
            topic_subscribers.remove(queue)
            if not topic_subscribers:
                SUBSCRIBERS.pop(topic, None)


async def stream_topic_events(
    topic: str, queue: asyncio.Queue[str]
) -> AsyncIterator[Dict[str, str]]:
    try:
        history = await snapshot_topic_history(topic)
        for event in history:
            yield {"event": "message", "data": json.dumps(event)}

        while True:
            data = await queue.get()
            yield {"event": "message", "data": data}
    except asyncio.CancelledError:
        raise
    finally:
        await unregister_subscriber(topic, queue)


@app.get("/subscribe")
async def subscribe(topic: str):
    queue: asyncio.Queue[str] = asyncio.Queue()

    await register_subscriber(topic, queue)

    return EventSourceResponse(stream_topic_events(topic, queue))
