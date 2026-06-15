import requests
import numpy as np
import random
import time

API_URL = "http://127.0.0.1:8000/analyze"

# Feature indices (must match src/network/sniffer.py):
# 0: packet_len_norm  1: port_norm  2: ttl_norm  3: protocol_norm
# 4: flag_norm  5: time_norm  6: burst  7: port_risk  8: is_external


def _base_features():
    """Normal baseline features."""
    return [
        np.random.uniform(0.0, 0.3),   # 0: packet_len_norm
        np.random.uniform(0.0, 0.1),   # 1: port_norm (well-known port)
        np.random.uniform(0.3, 0.9),   # 2: ttl_norm
        np.random.uniform(0.0, 0.5),   # 3: protocol_norm (TCP/UDP)
        np.random.uniform(0.3, 0.6),   # 4: flag_norm (ACK)
        np.random.uniform(0.1, 0.5),   # 5: time_norm (normal gap)
        0,                              # 6: burst
        0,                              # 7: port_risk (well-known)
        np.random.choice([0, 1]),       # 8: is_external
    ]


# =============================
# FEATURE GENERATION
# =============================

def generate_features(mode="normal"):

    if mode == "attack":
        # SYN flood / port scan pattern
        return [
            np.random.uniform(0.0, 0.2),   # 0: small packets
            np.random.uniform(0.5, 1.0),   # 1: unusual ports
            np.random.uniform(0.1, 0.4),   # 2: low TTL (spoofed)
            0.33,                           # 3: TCP
            np.random.uniform(0.0, 0.2),   # 4: SYN flag (no ACK)
            np.random.uniform(0.0, 0.05),  # 5: very short inter-arrival
            1,                              # 6: burst detected
            np.random.uniform(0.6, 1.0),   # 7: high-risk port
            1,                              # 8: external
        ]

    elif mode == "anomaly":
        # subtle irregular behavior
        return [
            np.random.uniform(0.4, 0.8),   # 0: unusual packet size
            np.random.uniform(0.1, 0.5),   # 1: mixed ports
            np.random.uniform(0.2, 0.9),   # 2: varied TTL
            np.random.uniform(0.0, 0.7),   # 3: mixed protocols
            np.random.uniform(0.1, 0.7),   # 4: mixed flags
            np.random.uniform(0.05, 0.3),  # 5: moderate gap
            np.random.choice([0, 1]),       # 6: occasional burst
            np.random.uniform(0.2, 0.7),   # 7: medium port risk
            np.random.choice([0, 1]),       # 8: external
        ]

    else:
        return _base_features()


# =============================
# SEND TRAFFIC
# =============================

def send_traffic(mode="normal", ip=None):

    if not ip:
        ip = f"185.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"

    payload = {
        "features": generate_features(mode),
        "source_ip": ip,
        "destination_ip": "8.8.8.8"
    }

    try:
        response = requests.post(API_URL, json=payload, timeout=2)
        result = response.json()

        print(f"[{mode.upper()}] {ip} → {result}")

        return result

    except Exception as e:
        print("❌ API error:", e)
        return None


# =============================
# CONTINUOUS TRAFFIC
# =============================

def simulate_traffic(duration=30):

    print("🚀 Starting traffic simulation...")

    start = time.time()

    while time.time() - start < duration:

        r = random.random()

        if r < 0.7:
            send_traffic("normal")

        elif r < 0.9:
            send_traffic("attack")

        else:
            send_traffic("anomaly")  # rare anomaly

        time.sleep(0.2)

    print("✅ Simulation complete")


# =============================
# BURST ATTACK (🔥 IMPORTANT)
# =============================

def simulate_attack_burst(count=20):

    print("🚨 Launching attack burst...")

    ip = f"185.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"

    for _ in range(count):
        send_traffic("attack", ip=ip)  # same IP → persistence
        time.sleep(0.05)

    print("💥 Burst finished")


# =============================
# STEALTH / ANOMALY ATTACK
# =============================

def simulate_stealth_attack(count=30):

    print("🕵️ Stealth anomaly started...")

    ip = f"185.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"

    for _ in range(count):
        send_traffic("anomaly", ip=ip)
        time.sleep(random.uniform(0.3, 1.0))

    print("🧠 Stealth behavior complete")