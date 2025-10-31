
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any
import uuid
import time

app = FastAPI(title="Audit Agent (Stub ACL)")

class AuditEvent(BaseModel):
    tx_id: str
    event: str
    actor: str
    payload: Dict[str, Any]

LEDGER: list[dict] = []  # in-memory stub; replace with Azure Confidential Ledger

@app.post("/audit")
def audit(ev: AuditEvent):
    rec = {
        "ledger_id": str(uuid.uuid4()),
        "tx_id": ev.tx_id,
        "event": ev.event,
        "actor": ev.actor,
        "payload": ev.payload,
        "ts": time.time()
    }
    LEDGER.append(rec)
    return {"acl_txn": rec["ledger_id"], "proof": {"hash": rec["ledger_id"][-12:]}, "ts": rec["ts"]}

@app.get("/tx/{tx_id}")
def get_tx(tx_id: str):
    return [r for r in LEDGER if r["tx_id"] == tx_id]
