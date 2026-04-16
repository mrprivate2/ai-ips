import os
import time
from threading import Lock
import ipaddress


class BlacklistManager:

    def __init__(self, path="logs/blacklist.txt", ttl=300):

        self.path = path
        self.ttl = ttl  # seconds (auto-unblock)

        # ip → metadata
        self.blacklist = {}

        # subnet blocking
        self.subnets = set()

        self.lock = Lock()

        os.makedirs("logs", exist_ok=True)

        self._load()

    # ----------------------------------
    # LOAD EXISTING BLACKLIST
    # ----------------------------------
    def _load(self):

        if os.path.exists(self.path):
            try:
                with open(self.path, "r") as f:
                    for line in f:
                        ip = line.strip()
                        if ip:
                            self.blacklist[ip] = {
                                "timestamp": time.time(),
                                "reason": "Loaded from file",
                                "score": 0.5
                            }
            except Exception:
                pass

    # ----------------------------------
    # VALIDATE IP
    # ----------------------------------
    def _is_valid_ip(self, ip):

        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False

    # ----------------------------------
    # ADD IP
    # ----------------------------------
    def add_ip(self, ip, reason="Unknown", score=0.0):

        if not self._is_valid_ip(ip):
            return

        with self.lock:

            if ip in self.blacklist:
                return

            self.blacklist[ip] = {
                "timestamp": time.time(),
                "reason": reason,
                "score": score
            }

            # 🔥 SUBNET DETECTION (AUTO)
            try:
                subnet = str(ipaddress.ip_network(ip + "/24", strict=False))
                self.subnets.add(subnet)
            except Exception:
                pass

            try:
                with open(self.path, "a") as f:
                    f.write(ip + "\n")
            except Exception:
                pass

        print(f"🚫 IP BLACKLISTED: {ip} | Reason: {reason} | Score: {score:.2f}")

    # compatibility
    def add(self, ip):
        self.add_ip(ip)

    # ----------------------------------
    # CHECK BLACKLIST
    # ----------------------------------
    def is_blacklisted(self, ip):

        now = time.time()

        # direct IP check
        if ip in self.blacklist:

            entry = self.blacklist[ip]

            # TTL expiry
            if now - entry["timestamp"] > self.ttl:
                self.remove_ip(ip)
                return False

            return True

        # 🔥 SUBNET CHECK
        try:
            ip_obj = ipaddress.ip_address(ip)

            for subnet in self.subnets:
                if ip_obj in ipaddress.ip_network(subnet):
                    return True
        except Exception:
            pass

        return False

    # ----------------------------------
    # REMOVE IP
    # ----------------------------------
    def remove_ip(self, ip):

        with self.lock:

            if ip not in self.blacklist:
                return

            self.blacklist.pop(ip, None)

            try:
                with open(self.path, "w") as f:
                    for ip_addr in self.blacklist.keys():
                        f.write(ip_addr + "\n")
            except Exception:
                pass

        print(f"✅ IP UNBLOCKED: {ip}")

    # ----------------------------------
    # CLEAN EXPIRED IPS
    # ----------------------------------
    def cleanup(self):

        now = time.time()

        with self.lock:

            expired = [
                ip for ip, data in self.blacklist.items()
                if now - data["timestamp"] > self.ttl
            ]

            for ip in expired:
                self.blacklist.pop(ip, None)

    # ----------------------------------
    # CLEAR ALL (DEBUG)
    # ----------------------------------
    def clear(self):

        with self.lock:

            self.blacklist.clear()
            self.subnets.clear()

            try:
                with open(self.path, "w") as f:
                    f.write("")
            except Exception:
                pass

        print("🧹 Blacklist cleared")

    # ----------------------------------
    # GET ALL (FOR DASHBOARD)
    # ----------------------------------
    def get_all(self):

        return self.blacklist

    # ----------------------------------
    # GET SUBNETS (DEBUG)
    # ----------------------------------
    def get_subnets(self):

        return list(self.subnets)