import typer
import subprocess
import sys
import os
import json
from pathlib import Path
from src.cli.monitor import monitor_logs

app = typer.Typer(help="🛡 AI-IPS Cyber Defense Platform")

# Project root
BASE_DIR = Path(__file__).resolve().parents[2]


# ================================
# SETUP COMMAND
# ================================
@app.command()
def setup():
    """Initialize AI-IPS environment and configuration"""
    
    print("\n🛠  Setting up AI-IPS...")
    
    # Create necessary directories
    directories = ["logs", "logs/pcap", "src/models/saved", "configs"]
    for d in directories:
        path = BASE_DIR / d
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created directory: {d}")

    # Create default app_config.json if not exists
    config_path = BASE_DIR / "configs" / "app_config.json"
    if not config_path.exists():
        default_config = {
            "network_interface": "en0",
            "whitelist": ["127.", "192.168.", "10.", "172."],
            "debug": True,
            "block_ttl": 120,
            "log_file": "logs/security_events.jsonl",
            "blacklist_file": "logs/blacklist.txt"
        }
        with open(config_path, "w") as f:
            json.dump(default_config, f, indent=2)
        print("✅ Created default app_config.json")
    
    # Verify installation
    try:
        from src.install.installer import install_system
        install_system()
    except Exception as e:
        print(f"❌ Installation check failed: {e}")

    print("\n✨ Setup completed! You can now start the engine with 'sudo ai-ips start'")


# ================================
# START AI-IPS ENGINE
# ================================
@app.command()
def start():
    """Start the AI-IPS protection engine"""

    if os.getuid() != 0:
        print("❌ AI-IPS requires root privileges to sniff network traffic and manage firewall.")
        print("👉 Please run with: sudo ai-ips start")
        raise typer.Exit(code=1)

    print("🛡 Starting AI-IPS engine...")

    engine_path = BASE_DIR / "src" / "engine" / "network_engine.py"

    try:
        subprocess.run([sys.executable, str(engine_path)], check=True)
    except KeyboardInterrupt:
        print("\n🛑 AI-IPS stopped by user")
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
# SYSTEM STATUS
# ================================
@app.command()
def status():
    """Show AI-IPS status"""

    print("\n🛡 AI-IPS Status\n")

    app_config_path = BASE_DIR / "configs" / "app_config.json"
    if app_config_path.exists():
        with open(app_config_path) as f:
            app_config = json.load(f)
        logs_path = BASE_DIR / app_config.get("log_file", "logs/security_events.jsonl")
    else:
        logs_path = BASE_DIR / "logs" / "security_events.jsonl"
        
    model_path = BASE_DIR / "src" / "models" / "saved" / "supervised_model.pkl"

    print(f"Config:   {'OK' if app_config_path.exists() else 'Missing'}")
    print(f"Logs:     {'OK' if logs_path.exists() else 'Missing'}")
    print(f"Model:    {'Loaded' if model_path.exists() else 'Not Found'}")
    
    # Try to check if engine is running (basic check)
    try:
        import psutil
        engine_running = False
        for proc in psutil.process_iter(['cmdline']):
            if proc.info['cmdline'] and 'network_engine.py' in str(proc.info['cmdline']):
                engine_running = True
                break
        print(f"Engine:   {'Running' if engine_running else 'Stopped'}")
    except:
        pass


# ================================
# ENTRY POINT
# ================================
if __name__ == "__main__":
    app()
