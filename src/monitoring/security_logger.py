import json
import os
from datetime import datetime
from threading import Lock


class SecurityLogger:

    def __init__(self):

        self.log_file = "logs/security_events.json"
        os.makedirs("logs", exist_ok=True)

        self.lock = Lock()

        # ensure file exists
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                json.dump([], f)

    # =============================
    # LOG EVENT
    # =============================

    def log_event(self, event_type, source_ip, risk_level, attack_type, reasons=None):

        if not source_ip:
            return  # invalid entry

        if reasons is None:
            reasons = []

        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": str(event_type),
            "source_ip": str(source_ip),
            "risk_level": str(risk_level),
            "attack_type": str(attack_type),

            # 🔥 future-ready fields
            "reasons": reasons,
            "confidence": None,
            "suggestion": None
        }

        with self.lock:

            try:
                with open(self.log_file, "r") as f:
                    data = json.load(f)

                if not isinstance(data, list):
                    data = []

            except Exception:
                data = []

            data.append(event)

            # keep only latest logs
            if len(data) > 5000:
                data = data[-5000:]

            try:
                with open(self.log_file, "w") as f:
                    json.dump(data, f, indent=2)
            except Exception as e:
                print("[LOGGER] Write error:", e)