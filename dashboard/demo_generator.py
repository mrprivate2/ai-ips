import json
import random
import time
import os


ATTACK_TYPES = [
    "PORT_SCAN",
    "SYN_FLOOD",
    "DDOS",
    "TRAFFIC_ANOMALY"
]


def generate_attack():

    os.makedirs("logs", exist_ok=True)

    log_file = "logs/security_events.json"

    if not os.path.exists(log_file):
        with open(log_file, "w") as f:
            json.dump([], f)

    with open(log_file, "r") as f:
        data = json.load(f)

    attack = {
        "timestamp": time.time(),
        "source_ip": f"185.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
        "attack_type": random.choice(ATTACK_TYPES),
        "event_type": "BLOCKED",
        "risk_level": "HIGH"
    }

    data.append(attack)

    with open(log_file, "w") as f:
        json.dump(data, f, indent=2)

    print("⚡ Simulated attack added to logs")