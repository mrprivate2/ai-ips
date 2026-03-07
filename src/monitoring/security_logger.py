import json
import os
from datetime import datetime
from threading import Lock


class SecurityLogger:

    def __init__(self):

        self.log_file = "logs/security_events.json"
        os.makedirs("logs", exist_ok=True)

        self.lock = Lock()

        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                json.dump([], f)

    def log_event(self, event_type, source_ip, risk_level, attack_type, reasons=None):

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

            except:
                data = []

            data.append(event)

            data = data[-5000:]

            with open(self.log_file, "w") as f:
                json.dump(data, f, indent=2)