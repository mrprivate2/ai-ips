import sys
import socket
import json
import numpy as np
import time
from pathlib import Path
import threading
import os

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(BASE_DIR))

from src.detection.hybrid_detector import HybridDetector
from src.core.behavior_engine import BehaviorEngine
from src.network.sniffer import PacketSniffer
from src.security.blacklist_manager import BlacklistManager
from src.monitoring.security_logger import SecurityLogger
from src.ips.firewall import FirewallManager
from src.explainability.decision_explainer import explain_attack

from src.training.dataset_builder import save_sample
from src.training.training_scheduler import check_retraining

# 🌍 GLOBAL SYNC
from src.sync.global_threat_sync import push_attack, start_listener


# =============================
# LOAD CONFIGS
# =============================

def load_json(path):
    with open(path) as f:
        return json.load(f)

app_config_path = BASE_DIR / "configs" / "app_config.json"
model_config_path = BASE_DIR / "configs" / "model_config.json"

app_config = load_json(app_config_path)
model_config = load_json(model_config_path)

# =============================
# VALIDATE CONFIGS
# =============================

from src.utils.config_validator import validate_model_config, validate_app_config, validate_thresholds

if not validate_app_config(app_config):
    sys.exit(1)

if not validate_model_config(model_config):
    sys.exit(1)

validate_thresholds(model_config)

DEBUG = app_config.get("debug", True)
WHITELIST = app_config.get("whitelist", ["127.", "192.168.", "10.", "172."])
NETWORK_INTERFACE = app_config.get("network_interface", "en0")
BLOCK_TTL = app_config.get("block_ttl", 120)

# =============================
# GET LOCAL IP
# =============================

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except:
        return "127.0.0.1"
    finally:
        s.close()

LOCAL_IP = get_local_ip()

# =============================
# INIT COMPONENTS
# =============================

detector = HybridDetector(
    model_config["supervised_model_path"],
    model_config["unsupervised_model_path"],
    model_config
)

behavior_engine = BehaviorEngine()
firewall = FirewallManager()

blacklist = BlacklistManager(str(BASE_DIR / app_config.get("blacklist_file", "logs/blacklist.txt")))
security_logger = SecurityLogger()


# =============================
# 🌍 GLOBAL LISTENER THREAD
# =============================

threading.Thread(
    target=start_listener,
    args=(firewall, blacklist),
    daemon=True
).start()


print("\n🛡 AI-IPS LIVE PROTECTION STARTED")
print(f"📡 Monitoring Network Traffic on {LOCAL_IP}")
print(f"[AUTO] Interface: {NETWORK_INTERFACE}\n")


# =============================
# GLOBAL STATE
# =============================

last_log_time = 0
last_training_check = time.time()
last_cleanup_time = time.time()

recent_blocks = {}

def cleanup_blocks():
    global last_cleanup_time
    now = time.time()
    if now - last_cleanup_time < 10:  # Throttle cleanup
        return
        
    for ip in list(recent_blocks.keys()):
        if now - recent_blocks[ip] > BLOCK_TTL:
            recent_blocks.pop(ip, None)
    
    last_cleanup_time = now


# =============================
# PACKET HANDLER
# =============================

def handle_packet(features, src_ip, dst_ip, dst_port, tcp_flag, packet):

    global last_log_time, last_training_check

    try:
        # ✅ SAFE CHECK
        if features is None or len(features) == 0:
            return

        # =============================
        # BASIC FILTERING
        # =============================

        if src_ip == LOCAL_IP or dst_ip != LOCAL_IP:
            return

        if any(src_ip.startswith(w) for w in WHITELIST):
            return

        if blacklist.is_blacklisted(src_ip):
            return

        if DEBUG:
            # Throttle debug prints to avoid flooding
            if time.time() - last_log_time > 0.1:
                print(f"[DEBUG] {src_ip} → {dst_ip} | Port {dst_port} | Flag {tcp_flag}")

        try:
            dst_port = int(dst_port)
        except:
            dst_port = 0

        # =============================
        # BEHAVIOR ANALYSIS
        # =============================

        behavior = behavior_engine.analyze(src_ip, dst_port, tcp_flag)
        behavioral_risk = behavior.get("risk", 0.0)
        behavior_type = behavior.get("attack_type", "NORMAL")

        # =============================
        # AI ANALYSIS (FIXED FEATURE MATCH)
        # =============================

        ai_risk = 0.0
        ai_type = "NORMAL"

        try:
            # ✅ Pass all features from sniffer to detector
            result = detector.detect(features)

            ai_risk = result.get("final_threat_score", 0.0)
            ai_type = result.get("attack_type", "NORMAL")

        except Exception as e:
            if DEBUG:
                print("[AI ERROR]", e)

        # =============================
        # FINAL DECISION
        # =============================

        final_risk = max(behavioral_risk, ai_risk)
        attack_type = behavior_type if behavioral_risk >= ai_risk else ai_type

        # =============================
        # SELF LEARNING (Throttled)
        # =============================

        if final_risk > 0.3 or np.random.random() < 0.05: # Save interesting samples or 5% of normal
            try:
                save_sample(features, attack_type)
            except:
                pass

        if time.time() - last_training_check > 300: # Check every 5 mins
            try:
                check_retraining()
            except:
                pass
            last_training_check = time.time()

        cleanup_blocks()

        # =============================
        # BLOCKING LOGIC
        # =============================

        if final_risk >= model_config.get("block_threshold", 0.65):

            if src_ip in recent_blocks:
                return

            recent_blocks[src_ip] = time.time()

            explanation = explain_attack(features, attack_type)

            print(f"🚫 [BLOCKED] {src_ip} — {attack_type} (Risk: {final_risk:.2f})")

            if explanation:
                print("   Reason:", explanation)

            firewall.block_ip(src_ip)
            blacklist.add_ip(src_ip, reason=attack_type, score=final_risk)

            try:
                push_attack(src_ip, attack_type, int(final_risk * 10))
            except:
                pass

            security_logger.log_event(
                "BLOCKED",
                src_ip,
                "HIGH",
                attack_type,
                reasons=[explanation] if explanation else []
            )

        elif final_risk >= model_config.get("warning_threshold", 0.40):

            now = time.time()

            if now - last_log_time > 2: # Warning throttle
                print(f"⚠️ [WARNING] {src_ip} — {attack_type} (Risk: {final_risk:.2f})")
                last_log_time = now

                security_logger.log_event(
                    "WARNING",
                    src_ip,
                    "MEDIUM",
                    attack_type
                )

    except Exception as e:
        if DEBUG:
            print("Packet processing error:", e)


# =============================
# SNIFFER LOOP
# =============================

def start_sniffer():

    print(f"[SNIFFER] Listening on interface: {NETWORK_INTERFACE}")

    while True:
        try:
            sniffer = PacketSniffer(interface=NETWORK_INTERFACE)
            sniffer.capture(handle_packet)

        except Exception as e:
            print("⚠ Sniffer crashed:", e)
            print("Restarting in 2s...")
            time.sleep(2)


# =============================
# ENTRY POINT
# =============================

if __name__ == "__main__":
    
    if os.getuid() != 0:
        print("❌ AI-IPS requires root privileges. Please run with sudo.")
        sys.exit(1)

    try:
        start_sniffer()

    except KeyboardInterrupt:
        print("\n🛑 AI-IPS stopped by user")
        print("Shutting down safely...")
