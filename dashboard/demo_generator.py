import json
import random
import time
import os
from datetime import datetime


# =============================
# ATTACK TYPES (REALISTIC)
# =============================

ATTACK_TYPES = [
    "PORT_SCAN",
    "SYN_FLOOD",
    "DDOS",
    "TRAFFIC_ANOMALY",
    "NORMAL"
]

RISK_LEVELS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
EVENT_TYPES = ["BLOCKED", "WARNING"]


# =============================
# GENERATE RANDOM PUBLIC IP
# =============================

def generate_ip():
    return f"{random.randint(1,223)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"


# =============================
# LOAD LOG FILE
# =============================

LOG_FILE = "logs/security_events.jsonl"


def load_log():

    os.makedirs("logs", exist_ok=True)
    events = []

    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as f:
                for line in f:
                    if line.strip():
                        events.append(json.loads(line))
        except Exception:
            pass

    return events


def save_log(data):

    with open(LOG_FILE, "w") as f:
        for event in data:
            f.write(json.dumps(event) + "\n")


# =============================
# GENERATE ATTACK EVENT
# =============================

def generate_attack(ip=None, attack_type=None):

    data = load_log()

    # reuse IP → simulate persistence
    if not ip:
        ip = generate_ip()

    if not attack_type:
        attack_type = random.choice(ATTACK_TYPES)

    # =========================
    # BEHAVIOR BASED LOGIC
    # =========================

    if attack_type == "DDOS":
        risk = "CRITICAL"
        event = "BLOCKED"

    elif attack_type == "PORT_SCAN":
        risk = "HIGH"
        event = "WARNING"

    elif attack_type == "TRAFFIC_ANOMALY":
        risk = "HIGH"
        event = "WARNING"
        attack_type = "UNKNOWN_THREAT"   # 🔥 anomaly mapping

    elif attack_type == "NORMAL":
        risk = "LOW"
        event = "INFO"

    else:
        risk = random.choice(RISK_LEVELS)
        event = random.choice(EVENT_TYPES)

    attack = {
        "timestamp": datetime.utcnow().isoformat(),
        "source_ip": ip,
        "attack_type": attack_type,
        "event_type": event,
        "risk_level": risk
    }

    data.append(attack)
    save_log(data)

    print(f"⚡ {attack_type} from {ip}")


# =============================
# BURST SIMULATION
# =============================

def simulate_attack_burst(count=10, delay=0.3):

    print(f"🚨 Burst: {count} events")

    ip = generate_ip()  # same IP → persistence

    for _ in range(count):
        generate_attack(ip=ip, attack_type="DDOS")
        time.sleep(delay)

    print("✅ Burst complete")


# =============================
# MIXED TRAFFIC SIMULATION
# =============================

def simulate_mixed_traffic(count=20, delay=0.5):

    print("🌐 Simulating mixed traffic...")

    for _ in range(count):

        attack_type = random.choice(ATTACK_TYPES)

        if attack_type == "PORT_SCAN":
            # repeated IP behavior
            ip = generate_ip()
            for _ in range(3):
                generate_attack(ip=ip, attack_type="PORT_SCAN")

        else:
            generate_attack(attack_type=attack_type)

        time.sleep(delay)

    print("✅ Simulation complete")