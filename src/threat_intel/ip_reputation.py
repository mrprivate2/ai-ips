import requests
import time


class IPReputationChecker:

    def __init__(self):

        self.cache = {}  # ip → data
        self.cache_ttl = 3600  # 1 hour

    # ---------------------------------------
    # CHECK IP REPUTATION
    # ---------------------------------------
    def check_ip(self, ip):

        now = time.time()

        # =============================
        # CACHE CHECK
        # =============================

        if ip in self.cache:

            cached = self.cache[ip]

            if now - cached["timestamp"] < self.cache_ttl:
                return cached["data"]

        # =============================
        # API LOOKUP
        # =============================

        country = "Unknown"
        org = "Unknown"

        try:

            url = f"http://ip-api.com/json/{ip}?fields=country,org"

            r = requests.get(url, timeout=2)
            data = r.json()

            country = data.get("country", "Unknown")
            org = data.get("org", "Unknown")

        except Exception:
            pass

        # =============================
        # RISK SCORING
        # =============================

        score = 0
        malicious = False

        # 🔥 suspicious hosting providers
        suspicious_org_keywords = [
            "hosting",
            "cloud",
            "vps",
            "digitalocean",
            "aws",
            "azure"
        ]

        if any(k.lower() in org.lower() for k in suspicious_org_keywords):
            score += 30

        # 🔥 unknown / hidden org
        if org == "Unknown":
            score += 20

        # 🔥 rare geo (light signal only)
        high_risk_regions = ["North Korea"]

        if country in high_risk_regions:
            score += 40

        # clamp score
        score = min(score, 100)

        if score >= 50:
            malicious = True

        result = {
            "malicious": malicious,
            "country": country,
            "org": org,
            "score": score
        }

        # =============================
        # CACHE STORE
        # =============================

        self.cache[ip] = {
            "timestamp": now,
            "data": result
        }

        return result