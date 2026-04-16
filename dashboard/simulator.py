import requests
import numpy as np
import random
import time

API_URL = "http://127.0.0.1:8000/analyze"


# =============================
# FEATURE GENERATION
# =============================

def generate_features(mode="normal"):

    if mode == "attack":
        # high intensity pattern
        return np.random.uniform(0.7, 1.0, 41).tolist()

    elif mode == "anomaly":
        # irregular behavior
        return np.random.uniform(0.2, 0.8, 41).tolist()

    else:
        # normal traffic
        return np.random.uniform(0.0, 0.3, 41).tolist()


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