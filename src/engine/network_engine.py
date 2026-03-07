import sys
import socket
import json
import numpy as np
import time
import psutil
from pathlib import Path

# =============================
# PROJECT ROOT
# =============================

BASE_DIR = Path(__file__).resolve().parents[2]

sys.path.append(str(BASE_DIR))


# =============================
# IMPORT MODULES
# =============================

from src.detection.hybrid_detector import HybridDetector
from src.core.behavior_engine import BehaviorEngine
from src.network.sniffer import PacketSniffer
from src.security.blacklist_manager import BlacklistManager
from src.security.unblock_manager import UnblockManager
from src.monitoring.security_logger import SecurityLogger
from src.ips.firewall import FirewallManager
from src.explainability.decision_explainer import explain_attack

from src.training.dataset_builder import save_sample
from src.training.training_scheduler import check_retraining


# =============================
# WHITELIST
# =============================

WHITELIST = [
    "127.",
    "192.168.",
    "10.",
    "172.16.",
    "8.8.8.8",
    "1.1.1.1"
]


# =============================
# GET LOCAL IP
# =============================

def get_local_ip():

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip


LOCAL_IP = get_local_ip()


# =============================
# DETECT NETWORK INTERFACE
# =============================

def detect_interface():

    try:

        for interface, addrs in psutil.net_if_addrs().items():

            for addr in addrs:

                if addr.family == socket.AF_INET and addr.address == LOCAL_IP:
                    return interface

    except Exception:
        pass

    return "en0"


NETWORK_INTERFACE = detect_interface()


# =============================
# LOAD CONFIG
# =============================

config_path = BASE_DIR / "configs" / "model_config.json"

with open(config_path) as f:
    config = json.load(f)


# =============================
# INITIALIZE COMPONENTS
# =============================

detector = HybridDetector(
    config["supervised_model_path"],
    config["unsupervised_model_path"],
    config
)

behavior_engine = BehaviorEngine()

firewall = FirewallManager()

blacklist = BlacklistManager(
    BASE_DIR / "logs" / "blacklist.txt"
)

unblock_manager = UnblockManager(
    firewall,
    blacklist,
    duration=300
)

security_logger = SecurityLogger()


print("\n🛡 AI-IPS LIVE PROTECTION STARTED")
print(f"📡 Monitoring Network Traffic on {LOCAL_IP}")
print(f"[AUTO] Using interface: {NETWORK_INTERFACE}\n")


# =============================
# RATE LIMIT TERMINAL LOGS
# =============================

last_log_time = 0
recent_blocks = {}
last_training_check = time.time()


# =============================
# PACKET HANDLER
# =============================

def handle_packet(features, src_ip, dst_ip, dst_port, tcp_flag):

    global last_log_time
    global last_training_check

    try:

        if features is None:
            return

        if src_ip == LOCAL_IP:
            return

        if any(src_ip.startswith(w) for w in WHITELIST):
            return

        if blacklist.is_blacklisted(src_ip):
            return

        # Behavior analysis
        behavior = behavior_engine.analyze(
            src_ip,
            dst_port,
            tcp_flag
        )

        behavioral_risk = behavior.get("risk", 0.0)
        attack_type = behavior.get("attack_type", "UNKNOWN")

        # AI detection
        ai_risk = 0.0

        try:
            result = detector.detect(np.array([features]))
            ai_risk = result.get("final_threat_score", 0.0)
        except Exception:
            pass

        final_risk = max(behavioral_risk, ai_risk)

        # Self learning
        try:
            save_sample(features, attack_type)
        except Exception:
            pass

        if time.time() - last_training_check > 30:

            try:
                check_retraining()
            except Exception:
                pass

            last_training_check = time.time()

        # Decision engine
        if final_risk >= 0.65:

            if src_ip in recent_blocks:
                return

            recent_blocks[src_ip] = time.time()

            explanation = explain_attack(features, attack_type)

            print(f"[BLOCKED] {src_ip} — {attack_type}")

            if explanation:
                print("Reason:")
                print(explanation)

            firewall.block_ip(src_ip)
            blacklist.add_ip(src_ip)
            unblock_manager.block_with_timer(src_ip)

            security_logger.log_event(
                "BLOCKED",
                src_ip,
                "HIGH",
                attack_type
            )

        elif final_risk >= 0.40:

            now = time.time()

            if now - last_log_time > 1:

                print(f"[WARNING] {src_ip} — {attack_type}")
                last_log_time = now

            security_logger.log_event(
                "WARNING",
                src_ip,
                "MEDIUM",
                attack_type
            )

    except Exception as e:

        print("Packet processing error:", e)


# =============================
# START SNIFFER
# =============================

def start_sniffer():

    global NETWORK_INTERFACE

    try:

        while True:

            try:

                NETWORK_INTERFACE = detect_interface()

                print(f"\n[SNIFFER] Listening on interface: {NETWORK_INTERFACE}")

                sniffer = PacketSniffer(interface=NETWORK_INTERFACE)

                sniffer.capture(handle_packet)

            except Exception:

                print("\n⚠ Network interface changed. Restarting sniffer...")
                time.sleep(3)

    except KeyboardInterrupt:

        print("\n🛑 AI-IPS stopped by user")
        print("Shutting down safely...")


# =============================
# START SYSTEM
# =============================

if __name__ == "__main__":

    start_sniffer()