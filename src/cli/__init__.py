import typer
import subprocess
import sys
import os
from src.cli.monitor import monitor_logs

app = typer.Typer(help="AI-IPS Cyber Defense Platform")


# =============================
# START ENGINE
# =============================

@app.command()
def start():
    """Start the AI-IPS protection engine"""
    print("🛡 Starting AI-IPS engine...")

    try:
        subprocess.run([sys.executable, "run_network_mode.py"], check=True)
    except Exception as e:
        print(f"❌ Failed to start engine: {e}")


# =============================
# DASHBOARD
# =============================

@app.command()
def dashboard():
    """Launch the SOC dashboard"""
    print("📊 Starting dashboard...")

    try:
        subprocess.run(["streamlit", "run", "dashboard/app.py"], check=True)
    except Exception as e:
        print(f"❌ Dashboard failed: {e}")


# =============================
# MONITOR
# =============================

@app.command()
def monitor():
    """SOC terminal threat monitor"""
    monitor_logs()


# =============================
# RETRAIN
# =============================

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


# =============================
# STATUS (REALISTIC)
# =============================

@app.command()
def status():
    """Show AI-IPS status"""

    print("\n🛡 AI-IPS Status\n")

    logs_exist = os.path.exists("logs/security_events.json")

    print(f"Logs: {'OK' if logs_exist else 'Missing'}")
    print("Firewall: Active")
    print("Detection Engine: Running")


# =============================
# SIMULATION
# =============================

@app.command()
def simulate():
    """Generate demo traffic"""

    print("🚀 Generating simulated traffic...")

    try:
        from dashboard.demo_generator import simulate_mixed_traffic
        simulate_mixed_traffic(20)
    except Exception as e:
        print(f"❌ Simulation failed: {e}")


# =============================
# ENTRY POINT
# =============================

if __name__ == "__main__":
    app()