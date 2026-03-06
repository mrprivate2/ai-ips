import requests

class ThreatIntelEngine:

    def __init__(self):
        self.sources = [
            "https://ipapi.co",
            "https://ipwho.is"
        ]

    def enrich_ip(self, ip):

        try:
            r = requests.get(f"https://ipapi.co/{ip}/json/", timeout=3)
            data = r.json()

            return {
                "ip": ip,
                "country": data.get("country_name"),
                "org": data.get("org"),
                "asn": data.get("asn")
            }

        except:
            return {"ip": ip, "country": "Unknown"}