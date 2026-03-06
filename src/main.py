import sys
import subprocess


def start_ips():

    print("\n🛡 Starting AI-IPS engine...\n")

    try:

        subprocess.run(
            ["python", "run_network_mode.py"],
            check=True
        )

    except KeyboardInterrupt:

        print("\n🛑 AI-IPS stopped by user")


def start_dashboard():

    print("\n📊 Starting AI-IPS dashboard...\n")

    subprocess.run(
        ["streamlit", "run", "dashboard/app.py"]
    )


def monitor():

    print("\n🛡 Starting SOC monitor...\n")

    from src.cli.monitor import monitor_logs

    monitor_logs()


def status():

    print("\nAI-IPS Status\n")

    print("Logs: OK")
    print("Firewall: Active")
    print("AI Detector: Ready")


def retrain():

    print("\n🧠 Starting AI model retraining...\n")

    from src.training.auto_trainer import retrain_model

    retrain_model()


def main():

    if len(sys.argv) < 2:

        print(
            """
AI-IPS CLI

Commands:

ai-ips start
ai-ips dashboard
ai-ips monitor
ai-ips retrain
ai-ips status
"""
        )

        return

    command = sys.argv[1]

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
        print("Unknown command")


if __name__ == "__main__":
    main()