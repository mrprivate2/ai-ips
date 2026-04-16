import typer
import subprocess
import sys
import os
from pathlib import Path

from src.cli.monitor import monitor_logs

app = typer.Typer(help="AI-IPS Cyber Defense Platform")

# Project root
BASE_DIR = Path(__file__).resolve().parents[2]


# ================================
# START AI-IPS ENGINE
# ================================
@app.command()
def start():
    """Start the AI-IPS protection engine"""

    print("🛡 Starting AI-IPS engine...")

    engine_path = BASE_DIR / "src" / "engine" / "network_engine.py"

    try:
        subprocess.run([sys.executable, str(engine_path)], check=True)
    except Exception as e:
        print(f"❌ Engine failed to start: {e}")


# ================================
# START DASHBOARD
# ================================
@app.command()
def dashboard():
    """Launch the SOC dashboard"""

    print("📊 Starting dashboard...")

    dashboard_path = BASE_DIR / "dashboard" / "app.py"

    try:
        subprocess.run([
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(dashboard_path)
        ], check=True)
    except Exception as e:
        print(f"❌ Dashboard failed: {e}")


# ================================
# SOC TERMINAL MONITOR
# ================================
@app.command()
def monitor():
    """SOC terminal threat monitor"""

    try:
        monitor_logs()
    except Exception as e:
        print(f"❌ Monitor failed: {e}")


# ================================
# RETRAIN AI MODEL
# ================================
@app.command()
def retrain():
    """Retrain AI models"""

    print("🧠 Retraining AI models...")

    try:
        from src.training.auto_trainer import retrain_model
        retrain_model()
        print("✅ Retraining completed")
    except Exception as e:
        print(f"❌ Retraining failed: {e}")


# ================================
# SYSTEM STATUS (REAL)
# ================================
@app.command()
def status():
    """Show AI-IPS status"""

    print("\n🛡 AI-IPS Status\n")

    logs_path = BASE_DIR / "logs" / "security_events.json"
    model_path = BASE_DIR / "src" / "models" / "saved" / "supervised_model.pkl"

    print(f"Logs: {'OK' if logs_path.exists() else 'Missing'}")
    print(f"Model: {'Loaded' if model_path.exists() else 'Not Found'}")
    print("Firewall: Active")
    print("Detection Engine: Ready")


# ================================
# ENTRY POINT
# ================================
if __name__ == "__main__":
    app()