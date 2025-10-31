
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="Dashboard")

HTML = '''
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>IG&S Phase 3 – Dashboard</title>
  <style>
    body { font-family: ui-sans-serif, system-ui, Arial; margin: 2rem; }
    .row { border: 1px solid #ddd; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; }
    .meta { font-size: 12px; color: #666; }
    code { background: #f6f8fa; padding: .25rem .5rem; border-radius: 4px; }
    .pill { display: inline-block; padding: .1rem .5rem; border: 1px solid #bbb; border-radius: 999px; font-size: 12px; }
  </style>
</head>
<body>
  <h1>IG&S Phase 3 – Day‑1 MVP</h1>
  <p class="meta">Streaming intents from Relay and showing decisions. Start Relay (8001), Policy (8002), Audit (8003) first.</p>
  <div id="feed"></div>
  <script>
    const feed = document.getElementById('feed');
    const es = new EventSource('http://localhost:8001/subscribe?topic=access.intent');
    es.onmessage = async (evt) => {
      const e = JSON.parse(evt.data);
      const intent = e.payload;
      const d = await fetch('http://localhost:8002/evaluate', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify(intent)
      }).then(r => r.json());
      await fetch('http://localhost:8003/audit', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({tx_id: d.tx_id, event: 'policy.decision', actor: 'policy', payload: d})
      });
      const div = document.createElement('div');
      div.className = 'row';
      div.innerHTML = `
        <div><span class="pill">${d.decision.toUpperCase()}</span> <code>${d.tx_id}</code></div>
        <pre>${JSON.stringify(intent, null, 2)}</pre>
        <pre>${JSON.stringify(d, null, 2)}</pre>
      `;
      feed.prepend(div);
    };
  </script>
</body>
</html>
'''

@app.get("/", response_class=HTMLResponse)
def index():
    return HTML
