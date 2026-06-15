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

        database_url = os.environ.get("FIREBASE_DATABASE_URL", "")
        if not database_url:
            print("[FIREBASE] FIREBASE_DATABASE_URL not set → running in offline mode")
            return None

        cred = credentials.Certificate(key_path)

        firebase_admin.initialize_app(cred, {
            "databaseURL": database_url
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
        # 🔥 Firebase keys cannot contain '.'
        sanitized_ip = ip.replace(".", "_")

        ref.child(sanitized_ip).set({
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

    try:
        ref = init_firebase()

        if ref is None:
            print("[FIREBASE] Listener disabled (no connection)")
            return

        print("[FIREBASE] Global sync listener started")

        def listener(event):
            try:
                # 🔥 Convert back from sanitized IP
                ip_raw = event.path.strip("/")
                if not ip_raw: return
                
                ip = ip_raw.replace("_", ".")
                
                data = event.data
                if not isinstance(data, dict): return

                score = data.get("score", 0)
                attack_type = data.get("attack_type", "GLOBAL_THREAT")

                if score >= 5 and not blacklist.is_blacklisted(ip):
                    print(f"[GLOBAL BLOCK] {ip} — {attack_type} (score={score})")
                    firewall.block_ip(ip)
                    blacklist.add_ip(ip, reason=f"GLOBAL:{attack_type}", score=score / 10.0)

            except Exception as e:
                print("[FIREBASE] Listener logic error:", e)

        # Establish SSE connection (blocks until connected or fails)
        ref.listen(listener)

    except Exception as e:
        print(f"⚠️  [FIREBASE] Connection failed: {e}")
        print("💡 Running in local-only mode. (Check your internet or Firebase config)")