
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any
from sse_starlette.sse import EventSourceResponse
import asyncio
import json
import time
import uuid

app = FastAPI(title="Relay")

SUBSCRIBERS = []  # naive in-memory for MVP
EVENTS: List[Dict[str, Any]] = []

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
    EVENTS.append(evt)
    data = json.dumps(evt)
    for q in SUBSCRIBERS:
        await q.put(data)
    return {"status": "ok", "event_id": evt["id"]}

@app.get("/subscribe")
async def subscribe(topic: str = "access.intent"):
    q: asyncio.Queue = asyncio.Queue()
    SUBSCRIBERS.append(q)

    async def event_generator():
        try:
            for e in EVENTS[-50:]:
                if e["topic"] == topic:
                    yield {"event": "message", "data": json.dumps(e)}
            while True:
                data = await q.get()
                evt = json.loads(data)
                if evt["topic"] == topic:
                    yield {"event": "message", "data": data}
        except asyncio.CancelledError:
            pass
        finally:
            SUBSCRIBERS.remove(q)

    return EventSourceResponse(event_generator())
