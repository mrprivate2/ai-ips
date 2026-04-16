import os
import subprocess
import platform
import sys


def run_command(cmd):
    try:
        subprocess.run(cmd, check=True)
        return True
    except Exception as e:
        print(f"❌ Failed: {' '.join(cmd)}")
        print("Error:", e)
        return False


def install_system():

    print("🛡 Installing AI-IPS dependencies...\n")

    system = platform.system()

    # =============================
    # SYSTEM DEPENDENCIES
    # =============================

    print("🔧 Installing system tools...")

    if system == "Linux":
        run_command(["sudo", "apt", "update"])
        run_command(["sudo", "apt", "install", "tcpdump", "-y"])

    elif system == "Darwin":
        # check if brew exists
        if subprocess.call(["which", "brew"], stdout=subprocess.DEVNULL) == 0:
            run_command(["brew", "install", "tcpdump"])
        else:
            print("⚠ Homebrew not found. Install it first: https://brew.sh")

    elif system == "Windows":
        print("⚠ Windows detected")
        print("Install Npcap manually: https://npcap.com/#download")

    else:
        print("⚠ Unsupported OS")

    # =============================
    # PYTHON DEPENDENCIES
    # =============================

    print("\n📦 Installing Python dependencies...")

    run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

    # =============================
    # CREATE FOLDERS
    # =============================

    print("\n📁 Creating folders...")

    os.makedirs("logs", exist_ok=True)
    os.makedirs("logs/pcap", exist_ok=True)

    print("\n✔ Installation completed successfully!")