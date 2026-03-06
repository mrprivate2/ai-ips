import json
import time
import os
from datetime import datetime

LOG_FILE = "logs/security_events.json"


def format_time(ts):
    try:
        return datetime.fromisoformat(ts).strftime("%H:%M:%S")
    except:
        return "N/A"


def monitor_logs():

    print("\n🛡 AI-IPS SOC Monitor")
    print("=" * 65)
    print(f"{'TIME':<10}{'SOURCE IP':<18}{'ATTACK':<20}{'ACTION'}")
    print("=" * 65)

    last_seen = 0

    while True:

        if not os.path.exists(LOG_FILE):
            time.sleep(2)
            continue

        try:
            with open(LOG_FILE) as f:
                events = json.load(f)

        except:
            time.sleep(2)
            continue

        if len(events) > last_seen:

            new_events = events[last_seen:]

            for event in new_events:

                time_str = format_time(event.get("timestamp", ""))
                ip = event.get("source_ip", "Unknown")
                attack = event.get("attack_type", "Unknown")
                action = event.get("event_type", "")

                print(
                    f"{time_str:<10}{ip:<18}{attack:<20}{action}"
                )

            last_seen = len(events)

        time.sleep(2)


if __name__ == "__main__":
    monitor_logs()
