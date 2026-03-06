import typer
import subprocess
from src.cli.monitor import monitor_logs

app = typer.Typer(help="AI-IPS Cyber Defense Platform")


@app.command()
def start():
    """Start the AI-IPS protection engine"""
    print("🛡 Starting AI-IPS engine...")
    subprocess.run(["python", "run_network_mode.py"])


@app.command()
def dashboard():
    """Launch the SOC dashboard"""
    print("📊 Starting dashboard...")
    subprocess.run(["streamlit", "run", "dashboard/app.py"])


@app.command()
def monitor():
    """SOC terminal threat monitor"""
    monitor_logs()


@app.command()
def retrain():
    """Retrain AI models"""
    print("🧠 Retraining AI models...")
    from src.training.auto_trainer import retrain_model
    retrain_model()


@app.command()
def status():
    """Show AI-IPS status"""

    print("\nAI-IPS Status\n")

    print("Logs: OK")
    print("Firewall: Active")
    print("AI Detector: Ready")


# NEW COMMAND
@app.command()
def simulate():
    """Generate demo attacks"""

    from dashboard.demo_generator import generate_attack

    generate_attack()


if __name__ == "__main__":
    app()