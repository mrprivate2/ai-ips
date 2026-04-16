import requests
import json
import time
from threading import Lock


class SensorAgent:

    def __init__(self, server, api_key=None):

        self.server = server.rstrip("/")
        self.api_key = api_key

        self.queue = []   # fallback queue
        self.lock = Lock()

    # ----------------------------------
    # SEND EVENT
    # ----------------------------------
    def send_event(self, event):

        headers = {"Content-Type": "application/json"}

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:

            response = requests.post(
                f"{self.server}/event",
                json=event,
                headers=headers,
                timeout=2
            )

            if response.status_code != 200:
                self._queue_event(event)

        except Exception:
            self._queue_event(event)

    # ----------------------------------
    # QUEUE EVENT (IF FAILED)
    # ----------------------------------
    def _queue_event(self, event):

        with self.lock:
            self.queue.append(event)

        print("[SENSOR] Event queued (server unreachable)")

    # ----------------------------------
    # RETRY QUEUED EVENTS
    # ----------------------------------
    def retry_queue(self):

        if not self.queue:
            return

        print(f"[SENSOR] Retrying {len(self.queue)} events...")

        with self.lock:

            remaining = []

            for event in self.queue:

                try:

                    response = requests.post(
                        f"{self.server}/event",
                        json=event,
                        timeout=2
                    )

                    if response.status_code != 200:
                        remaining.append(event)

                except Exception:
                    remaining.append(event)

            self.queue = remaining

    # ----------------------------------
    # BACKGROUND RETRY LOOP (OPTIONAL)
    # ----------------------------------
    def start_retry_loop(self, interval=5):

        def loop():
            while True:
                self.retry_queue()
                time.sleep(interval)

        import threading
        threading.Thread(target=loop, daemon=True).start()