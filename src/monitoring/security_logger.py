import json
import os
from datetime import datetime
from threading import Lock


class SecurityLogger:

    def __init__(self):

        self.log_file = "logs/security_events.json"

        os.makedirs("logs", exist_ok=True)

        # thread-safe writing
        self.lock = Lock()

        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                json.dump([], f)

    # ------------------------------------
    # LOG EVENT
    # ------------------------------------
    def log_event(self, event_type, source_ip, risk_level, attack_type, reasons=None):

        # allow backward compatibility
        if reasons is None:
            reasons = []

        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "source_ip": source_ip,
            "risk_level": risk_level,
            "attack_type": attack_type,
            "reasons": reasons
        }

        with self.lock:

            try:
                with open(self.log_file, "r") as f:
                    data = json.load(f)
            except Exception:
                data = []

            data.append(event)

            # keep last 5000 events
            data = data[-5000:]

            try:
                with open(self.log_file, "w") as f:
                    json.dump(data, f, indent=2)
            except Exception:
                pass