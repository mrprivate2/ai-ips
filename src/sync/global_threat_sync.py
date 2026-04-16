import firebase_admin
from firebase_admin import credentials, db
import time
import os


# =============================
# SAFE INIT (RUN ONCE)
# =============================

_initialized = False
_ref = None


def init_firebase():

    global _initialized, _ref

    if _initialized:
        return _ref

    try:
        key_path = "configs/firebase_key.json"

        if not os.path.exists(key_path):
            print("[FIREBASE] Key not found → running in offline mode")
            return None

        cred = credentials.Certificate(key_path)

        firebase_admin.initialize_app(cred, {
            "databaseURL": "https://ai-ips-3d2a0-default-rtdb.asia-southeast1.firebasedatabase.app"
        })

        _ref = db.reference("threats")
        _initialized = True

        print("[FIREBASE] Connected successfully")

        return _ref

    except Exception as e:
        print("[FIREBASE] Init error:", e)
        return None


# =============================
# PUSH ATTACK (SAFE)
# =============================

def push_attack(ip, attack_type, score):

    ref = init_firebase()

    if ref is None:
        return

    try:

        ref.child(ip).set({
            "score": score,
            "attack_type": attack_type,
            "timestamp": int(time.time())
        })

    except Exception as e:
        print("[FIREBASE] Push error:", e)


# =============================
# REAL-TIME LISTENER
# =============================

def start_listener(firewall, blacklist):

    ref = init_firebase()

    if ref is None:
        print("[FIREBASE] Listener disabled (no connection)")
        return

    print("[FIREBASE] Global sync listener started")

    def listener(event):

        try:

            ip = event.path.strip("/")

            if not ip:
                return

            data = event.data

            if not isinstance(data, dict):
                return

            score = data.get("score", 0)
            attack_type = data.get("attack_type", "GLOBAL_THREAT")

            # 🔥 Only block high-confidence threats
            if score >= 5 and not blacklist.is_blacklisted(ip):

                print(f"[GLOBAL BLOCK] {ip} — {attack_type} (score={score})")

                firewall.block_ip(ip)

                # 🔥 store reason + score
                blacklist.add_ip(
                    ip,
                    reason=f"GLOBAL:{attack_type}",
                    score=score / 10.0
                )

        except Exception as e:
            print("[FIREBASE] Listener error:", e)

    # 🔥 run listener
    ref.listen(listener)