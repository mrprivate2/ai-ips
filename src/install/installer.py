import os
import subprocess
import platform


def install_system():

    print("🛡 Installing AI-IPS dependencies...")

    system = platform.system()

    if system == "Linux":
        subprocess.run(["sudo", "apt", "install", "tcpdump", "-y"])

    elif system == "Darwin":
        subprocess.run(["brew", "install", "tcpdump"])

    print("Installing python dependencies...")
    subprocess.run(["pip", "install", "-r", "requirements.txt"])

    print("Creating log folders...")
    os.makedirs("logs", exist_ok=True)

    print("✔ Installation completed")