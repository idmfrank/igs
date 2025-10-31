
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any
import uuid
import time

app = FastAPI(title="Policy Agent")

class Intent(BaseModel):
    tx_id: str | None = None
    subject: Dict[str, Any]
    resource: Dict[str, Any]
    context: Dict[str, Any]

@app.post("/evaluate")
def evaluate(intent: Intent):
    allow = (
        intent.subject.get("enterprise") == "A"
        and intent.resource.get("enterprise") == "B"
        and intent.resource.get("scope") == "read"
        and intent.context.get("session_risk", 100) < 50
    )
    decision = "allow" if allow else "deny"
    tx_id = intent.tx_id or str(uuid.uuid4())
    return {
        "tx_id": tx_id,
        "decision": decision,
        "obligations": {"timebox": 3600} if allow else {},
        "risk_after": max(0, intent.context.get("session_risk", 50) - 5) if allow else intent.context.get("session_risk", 50),
        "explanation": "MVP rule evaluation without OPA; replace with real policy engine",
        "policy_ref": "policies/base.rego#rule-allow",
        "ts": time.time()
    }
