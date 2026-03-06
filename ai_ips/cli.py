import typer
from src.main import start_ips, start_dashboard, retrain, status
from src.cli.monitor import monitor_logs

app = typer.Typer(help="AI-IPS Cyber Defense Platform")


@app.command()
def start():
    """Start the AI-IPS network protection engine"""
    start_ips()


@app.command()
def dashboard():
    """Launch the SOC dashboard"""
    start_dashboard()


@app.command()
def monitor():
    """SOC terminal threat monitor"""
    monitor_logs()


@app.command()
def retrain():
    """Retrain the AI model"""
    retrain()


@app.command()
def status():
    """Show system status"""
    status()


if __name__ == "__main__":
    app()