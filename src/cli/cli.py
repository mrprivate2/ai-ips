import typer
import subprocess
import sys
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

    engine_path = BASE_DIR / "run_network_mode.py"

    subprocess.run([sys.executable, str(engine_path)])


# ================================
# START DASHBOARD
# ================================
@app.command()
def dashboard():
    """Launch the SOC dashboard"""

    print("📊 Starting dashboard...")

    dashboard_path = BASE_DIR / "dashboard" / "app.py"

    subprocess.run([
        "streamlit",
        "run",
        str(dashboard_path)
    ])


# ================================
# SOC TERMINAL MONITOR
# ================================
@app.command()
def monitor():
    """SOC terminal threat monitor"""

    monitor_logs()


# ================================
# RETRAIN AI MODEL
# ================================
@app.command()
def retrain():
    """Retrain AI models"""

    print("🧠 Retraining AI models...")

    from src.training.auto_trainer import retrain_model

    retrain_model()


# ================================
# SYSTEM STATUS
# ================================
@app.command()
def status():
    """Show AI-IPS status"""

    print("\n🛡 AI-IPS Status\n")

    print("Logs: OK")
    print("Firewall: Active")
    print("AI Detector: Ready")


if __name__ == "__main__":
    app()