
# IG&S Phase 3 – Federated Agent Mesh (Day‑1 MVP)

Minimal, platformless PoC that stitches together Python microservices, a lightweight relay,
an HTML dashboard, and a stubbed Azure Confidential Ledger writer.

Key characteristics:

- Python microservices for the relay, policy, audit, and dashboard roles
- Server‑Sent Events (SSE) fan‑out from the relay to the dashboard
- In‑memory audit log placeholder until Azure Confidential Ledger is integrated


## Quick start

```bash
# 1) Clone or unzip this repo locally, then:
python -m venv .venv && source .venv/bin/activate  # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt

# 2) Run all services (dev mode) on different ports
# Relay
uvicorn apps.relay.main:app --reload --port 8001
# Policy Agent
uvicorn apps.policy.main:app --reload --port 8002
# Audit Agent (stub for ACL write)
uvicorn apps.audit.main:app --reload --port 8003
# Dashboard
uvicorn apps.dashboard.main:app --reload --port 8004

# 3) Publish a sample access intent (in a separate shell)
python scripts/publish_intent.py
```

Open: `http://localhost:8004` for the dashboard.
You should see intents stream in as the relay fans them out, the policy agent evaluates
them, and the audit agent records the decisions.

## Minimal API map

- Relay: `POST /publish` | `GET /subscribe` (Server‑Sent Events)
- Policy: `POST /evaluate`
- Audit: `POST /audit`
- Dashboard: `/` (stream), `/tx/{id}` (detail)

### Relay publish & subscribe flow

- `POST /publish` accepts a JSON body matching `PublishPayload` (`{"topic": str, "payload": dict}`) and records the event in a per-topic, in-memory ring buffer (50 most recent entries).
- `GET /subscribe?topic=<name>` opens a Server-Sent Events stream that replays the stored history for the topic before forwarding new publishes in real time.
- Subscriber lifecycles are tracked with coroutine-safe locks so that disconnects automatically remove their queues.

Run the focused relay tests to confirm history replay and live fan-out behaviour:

```bash
pytest tests/relay/test_main.py
```

## Create the GitHub repo (two options)

**Option A – GitHub CLI (recommended):**
```bash
# requires: gh auth login
gh repo create igs-phase3-mvp --public --source . --remote origin --push
```

**Option B – Manual Git:**
```bash
git init
git add .
git commit -m "chore: bootstrap IG&S Phase 3 MVP"
git branch -M main
git remote add origin git@github.com:idmfrank/igs-phase3-mvp.git
git push -u origin main
```

## Next steps

- Wire the Audit Agent to Azure Confidential Ledger (replace the in-memory stub).
- Add mTLS between services and Key Vault-issued JWTs.
- Expand policies in `policies/base.rego` and add tests.
