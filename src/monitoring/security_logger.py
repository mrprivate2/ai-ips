import json
import os
from datetime import datetime
from threading import Lock
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

class SecurityLogger:

    def __init__(self, log_file=None):
        
        if log_file is None:
            # Try to load from config
            try:
                config_path = BASE_DIR / "configs" / "app_config.json"
                with open(config_path) as f:
                    config = json.load(f)
                self.log_file = str(BASE_DIR / config.get("log_file", "logs/security_events.jsonl"))
            except:
                self.log_file = str(BASE_DIR / "logs" / "security_events.jsonl")
        else:
            self.log_file = log_file

        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        self.lock = Lock()

    # =============================
    # LOG EVENT (JSONL format)
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
            "reasons": reasons,
            "confidence": None,
            "suggestion": None
        }

        with self.lock:
            try:
                with open(self.log_file, "a") as f:
                    f.write(json.dumps(event) + "\n")
            except Exception as e:
                print(f"[LOGGER] Write error: {e}")
