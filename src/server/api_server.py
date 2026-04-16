from fastapi import FastAPI, HTTPException, Request
from datetime import datetime

app = FastAPI()

# in-memory storage (simple SOC buffer)
events = []

MAX_EVENTS = 5000
API_KEY = "secret123"   # change this


# ----------------------------------
# RECEIVE EVENT
# ----------------------------------
@app.post("/event")
async def receive_event(request: Request, event: dict):

    # 🔐 SIMPLE AUTH
    auth = request.headers.get("Authorization")

    if auth != f"Bearer {API_KEY}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    # ⏱ ADD TIMESTAMP
    event["received_at"] = datetime.utcnow().isoformat()

    events.append(event)

    # 🔥 LIMIT MEMORY
    if len(events) > MAX_EVENTS:
        events.pop(0)

    return {"status": "ok"}


# ----------------------------------
# GET ALL EVENTS
# ----------------------------------
@app.get("/events")
def get_events(limit: int = 100):

    return events[-limit:]


# ----------------------------------
# FILTER EVENTS
# ----------------------------------
@app.get("/events/filter")
def filter_events(source_ip: str = None, attack_type: str = None):

    filtered = events

    if source_ip:
        filtered = [e for e in filtered if e.get("source_ip") == source_ip]

    if attack_type:
        filtered = [e for e in filtered if e.get("attack_type") == attack_type]

    return filtered[-100:]


# ----------------------------------
# CLEAR EVENTS (DEBUG)
# ----------------------------------
@app.delete("/events")
def clear_events():

    events.clear()
    return {"status": "cleared"}