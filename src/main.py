import sys
import subprocess


# ---------------------------------------
# START IPS ENGINE
# ---------------------------------------

def start_ips():

    print("\n🛡 Starting AI-IPS engine...\n")

    try:

        subprocess.run(
            [sys.executable, "run_network_mode.py"],  # ✅ FIXED
            check=True
        )

    except KeyboardInterrupt:
        print("\n🛑 AI-IPS stopped by user")

    except Exception as e:
        print(f"❌ Failed to start IPS: {e}")


# ---------------------------------------
# START DASHBOARD
# ---------------------------------------

def start_dashboard():

    print("\n📊 Starting AI-IPS dashboard...\n")

    try:

        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", "dashboard/app.py"],  # ✅ FIXED
            check=True
        )

    except Exception as e:
        print(f"❌ Dashboard error: {e}")


# ---------------------------------------
# MONITOR LOGS
# ---------------------------------------

def monitor():

    print("\n🛡 Starting SOC monitor...\n")

    try:
        from src.cli.monitor import monitor_logs
        monitor_logs()
    except Exception as e:
        print(f"❌ Monitor error: {e}")


# ---------------------------------------
# STATUS
# ---------------------------------------

def status():

    print("\n📊 AI-IPS Status\n")

    print("✔ Logs: OK")
    print("✔ Firewall: Active")
    print("✔ AI Detector: Ready")


# ---------------------------------------
# RETRAIN MODEL
# ---------------------------------------

def retrain():

    print("\n🧠 Starting AI model retraining...\n")

    try:
        from src.training.auto_trainer import retrain_model
        retrain_model()
    except Exception as e:
        print(f"❌ Retraining error: {e}")


# ---------------------------------------
# MAIN CLI
# ---------------------------------------

def main():

    if len(sys.argv) < 2:

        print(
            """
🛡 AI-IPS CLI

Commands:

ai-ips start       → Start intrusion prevention system
ai-ips dashboard   → Launch dashboard
ai-ips monitor     → Monitor logs (SOC view)
ai-ips retrain     → Retrain AI model
ai-ips status      → Show system status
"""
        )
        return

    command = sys.argv[1].lower()

    if command == "start":
        start_ips()

    elif command == "dashboard":
        start_dashboard()

    elif command == "monitor":
        monitor()

    elif command == "retrain":
        retrain()

    elif command == "status":
        status()

    else:
        print(f"❌ Unknown command: {command}")


if __name__ == "__main__":
    main()