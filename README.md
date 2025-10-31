
# IG&S Phase 3 – Federated Agent Mesh (Day‑1 MVP)

Minimal, platformless PoC: Python microservices + lightweight relay + Web dashboard + (stubbed) Azure Confidential Ledger writer.


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
```

Open: `http://localhost:8004` for the dashboard.

## Minimal API map

- Relay: `POST /publish`  | `GET /subscribe` (Server‑Sent Events)
- Policy: `POST /evaluate`
- Audit: `POST /audit`
- Dashboard: `/` (stream), `/tx/{id}` (detail)

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
- Wire the Audit Agent to Azure Confidential Ledger (replace stub).
- Add mTLS between services and Key Vault‑issued JWTs.
- Expand policies in `policies/base.rego` and add tests.
