import json
import time
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

def monitor_logs():
    # Load config to get log path
    config_path = BASE_DIR / "configs" / "app_config.json"
    log_file = BASE_DIR / "logs" / "security_events.jsonl"
    
    if config_path.exists():
        try:
            with open(config_path) as f:
                config = json.load(f)
                log_file = BASE_DIR / config.get("log_file", "logs/security_events.jsonl")
        except:
            pass

    print("\n🛡  AI-IPS SOC Monitor")
    print("=" * 70)
    print(f"{'TIME':<10}{'SOURCE IP':<18}{'ATTACK':<20}{'ACTION'}")
    print("=" * 70)

    try:
        if not os.path.exists(log_file):
            print(f"📡 Waiting for log file... ({log_file})")
            while not os.path.exists(log_file):
                time.sleep(1)

        with open(log_file, "r") as f:
            # Go to the end of the file
            f.seek(0, os.SEEK_END)
            
            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.5)
                    continue
                
                try:
                    event = json.loads(line)
                    event_type = event.get("event_type", "")
                    
                    if event_type not in ["WARNING", "BLOCKED"]:
                        continue

                    timestamp = event.get("timestamp", "")
                    time_str = timestamp[11:19] if len(timestamp) >= 19 else "N/A"

                    ip = event.get("source_ip", "Unknown")
                    attack = event.get("attack_type", "Unknown")

                    color_code = ""
                    if event_type == "BLOCKED":
                        color_code = "\033[91m" # Red
                    elif event_type == "WARNING":
                        color_code = "\033[93m" # Yellow
                    
                    reset_code = "\033[0m"

                    print(f"{time_str:<10}{ip:<18}{attack:<20}{color_code}{event_type}{reset_code}")
                except Exception:
                    continue

    except KeyboardInterrupt:
        print("\n🛑 Monitor stopped by user")
