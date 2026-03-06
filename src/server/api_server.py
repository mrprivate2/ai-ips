from fastapi import FastAPI

app = FastAPI()

events = []

@app.post("/event")
def receive_event(event: dict):

    events.append(event)
    return {"status": "ok"}

@app.get("/events")
def get_events():
    return events