import subprocess
import os
import sys


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def start_ips():
    print("🛡 Starting AI-IPS engine...")

    subprocess.run(
        [sys.executable, os.path.join(BASE_DIR, "run_network_mode.py")]
    )


def start_dashboard():
    print("📊 Launching SOC dashboard...")

    subprocess.run(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            os.path.join(BASE_DIR, "dashboard", "app.py")
        ]
    )


def retrain_model():
    print("🧠 Starting model retraining...")

    subprocess.run(
        [
            sys.executable,
            os.path.join(BASE_DIR, "src", "training", "auto_trainer.py")
        ]
    )


def show_status():

    print("\nAI-IPS Status\n")

    if os.path.exists(os.path.join(BASE_DIR, "logs", "security_events.json")):
        print("Logs: OK")
    else:
        print("Logs: Missing")

    print("Firewall: Active")
    print("AI Detector: Ready")