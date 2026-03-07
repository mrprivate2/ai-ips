import json
import time
import os


LOG_FILE = "logs/security_events.json"


def monitor_logs():

    print("\n🛡 AI-IPS SOC Monitor")
    print("=================================================================")
    print("TIME      SOURCE IP         ATTACK              ACTION")
    print("=================================================================")

    last_seen = 0

    while True:

        try:

            if not os.path.exists(LOG_FILE):
                time.sleep(1)
                continue

            with open(LOG_FILE, "r") as f:
                data = json.load(f)

            if len(data) > last_seen:

                new_events = data[last_seen:]

                for event in new_events:

                    # show only real security events
                    if event["event_type"] not in ["WARNING", "BLOCKED"]:
                        continue

                    timestamp = event["timestamp"][11:19]
                    ip = event["source_ip"]
                    attack = event["attack_type"]
                    action = event["event_type"]

                    print(f"{timestamp:<9} {ip:<16} {attack:<18} {action}")

                last_seen = len(data)

        except Exception:
            pass

        time.sleep(1)