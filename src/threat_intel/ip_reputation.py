import requests


class IPReputationChecker:

    def __init__(self):

        # optional API key
        self.abuseipdb_key = None

    # ---------------------------------------
    # CHECK MALICIOUS IP
    # ---------------------------------------

    def check_ip(self, ip):

        try:

            url = f"http://ip-api.com/json/{ip}"

            r = requests.get(url, timeout=2)

            data = r.json()

            country = data.get("country", "Unknown")

        except Exception:

            country = "Unknown"

        reputation = {
            "malicious": False,
            "country": country,
            "score": 0
        }

        # Example simple detection
        suspicious_countries = [
            "Russia",
            "China",
            "North Korea"
        ]

        if country in suspicious_countries:

            reputation["malicious"] = True
            reputation["score"] = 70

        return reputation