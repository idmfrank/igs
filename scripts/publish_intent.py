
#!/usr/bin/env python3
import httpx, uuid

intent = {
    "tx_id": str(uuid.uuid4()),
    "subject": {"enterprise": "A", "id": "u123", "roles": ["fin_analyst"]},
    "resource": {"enterprise": "B", "id": "dataset:finance.q4", "scope": "read"},
    "context": {"device": "compliant", "geo": "US", "session_risk": 42}
}

r = httpx.post("http://localhost:8001/publish", json={"topic": "access.intent", "payload": intent})
print(r.status_code, r.json())
