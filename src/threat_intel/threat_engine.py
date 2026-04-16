import requests
import time


class ThreatIntelEngine:

    def __init__(self):

        self.cache = {}
        self.cache_ttl = 3600  # 1 hour

    # ---------------------------------------
    # ENRICH IP WITH FALLBACK
    # ---------------------------------------
    def enrich_ip(self, ip):

        now = time.time()

        # =============================
        # CACHE CHECK
        # =============================

        if ip in self.cache:
            cached = self.cache[ip]
            if now - cached["timestamp"] < self.cache_ttl:
                return cached["data"]

        data = {}

        # =============================
        # SOURCE 1: ipapi.co
        # =============================

        try:

            r = requests.get(f"https://ipapi.co/{ip}/json/", timeout=2)
            res = r.json()

            data = {
                "ip": ip,
                "country": res.get("country_name", "Unknown"),
                "org": res.get("org", "Unknown"),
                "asn": res.get("asn", "Unknown")
            }

        except Exception:
            pass

        # =============================
        # SOURCE 2: ipwho.is (fallback)
        # =============================

        if not data or data.get("country") == "Unknown":

            try:

                r = requests.get(f"https://ipwho.is/{ip}", timeout=2)
                res = r.json()

                data = {
                    "ip": ip,
                    "country": res.get("country", "Unknown"),
                    "org": res.get("connection", {}).get("org", "Unknown"),
                    "asn": res.get("connection", {}).get("asn", "Unknown")
                }

            except Exception:
                pass

        # =============================
        # DEFAULT SAFE FALLBACK
        # =============================

        if not data:
            data = {
                "ip": ip,
                "country": "Unknown",
                "org": "Unknown",
                "asn": "Unknown"
            }

        # =============================
        # RISK SCORING
        # =============================

        score = 0

        org = data.get("org", "").lower()

        suspicious_keywords = [
            "hosting", "vps", "cloud", "digitalocean",
            "aws", "azure", "linode"
        ]

        if any(k in org for k in suspicious_keywords):
            score += 30

        if data["country"] in ["North Korea"]:
            score += 50

        score = min(score, 100)

        data["risk_score"] = score
        data["is_suspicious"] = score >= 50

        # =============================
        # CACHE STORE
        # =============================

        self.cache[ip] = {
            "timestamp": now,
            "data": data
        }

        return data