import json
import time
import os

LOG_FILE = "logs/security_events.json"


def monitor_logs():

    print("\n🛡 AI-IPS SOC Monitor")
    print("=" * 70)
    print(f"{'TIME':<10}{'SOURCE IP':<18}{'ATTACK':<20}{'ACTION'}")
    print("=" * 70)

    last_seen = 0

    try:
        while True:

            if not os.path.exists(LOG_FILE):
                time.sleep(1)
                continue

            try:
                with open(LOG_FILE, "r") as f:
                    data = json.load(f)
            except Exception:
                print("⚠ Error reading log file (possibly corrupted)")
                time.sleep(1)
                continue

            if not isinstance(data, list):
                time.sleep(1)
                continue

            if len(data) > last_seen:

                new_events = data[last_seen:]

                for event in new_events:

                    event_type = event.get("event_type", "")
                    
                    # show only relevant events
                    if event_type not in ["WARNING", "BLOCKED"]:
                        continue

                    timestamp = event.get("timestamp", "")
                    time_str = timestamp[11:19] if len(timestamp) >= 19 else "N/A"

                    ip = event.get("source_ip", "Unknown")
                    attack = event.get("attack_type", "Unknown")

                    print(f"{time_str:<10}{ip:<18}{attack:<20}{event_type}")

                last_seen = len(data)

            time.sleep(1)

    except KeyboardInterrupt:
        print("\n🛑 Monitor stopped by user")