import os
import subprocess
import platform
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

def run_command(cmd):
    try:
        subprocess.run(cmd, check=True)
        return True
    except Exception as e:
        print(f"❌ Failed: {' '.join(cmd)}")
        print("Error:", e)
        return False


def install_system():

    print("🛡  Verifying AI-IPS system dependencies...\n")

    system = platform.system()

    # =============================
    # SYSTEM DEPENDENCIES
    # =============================

    print("🔧 Checking system tools...")

    if system == "Linux":
        if subprocess.call(["which", "tcpdump"], stdout=subprocess.DEVNULL) != 0:
            print("📦 Installing tcpdump...")
            run_command(["sudo", "apt", "update"])
            run_command(["sudo", "apt", "install", "tcpdump", "-y"])
        else:
            print("✅ tcpdump already installed")

    elif system == "Darwin":
        if subprocess.call(["which", "tcpdump"], stdout=subprocess.DEVNULL) != 0:
            # check if brew exists
            if subprocess.call(["which", "brew"], stdout=subprocess.DEVNULL) == 0:
                print("📦 Installing tcpdump via Homebrew...")
                run_command(["brew", "install", "tcpdump"])
            else:
                print("⚠️  Homebrew not found. Please install tcpdump manually if needed.")
        else:
            print("✅ tcpdump already installed")

    elif system == "Windows":
        print("⚠️  Windows detected. Ensure Npcap is installed: https://npcap.com/#download")

    # =============================
    # PYTHON DEPENDENCIES
    # =============================

    print("\n📦 Verifying Python dependencies...")

    req_path = BASE_DIR / "requirements.txt"
    if req_path.exists():
        run_command([sys.executable, "-m", "pip", "install", "-r", str(req_path)])
    else:
        print("⚠️  requirements.txt not found in root directory.")

    # =============================
    # CREATE FOLDERS
    # =============================

    print("\n📁 Ensuring directories exist...")

    os.makedirs(BASE_DIR / "logs", exist_ok=True)
    os.makedirs(BASE_DIR / "logs/pcap", exist_ok=True)
    os.makedirs(BASE_DIR / "src/models/saved", exist_ok=True)

    print("\n✅ System check completed!")
