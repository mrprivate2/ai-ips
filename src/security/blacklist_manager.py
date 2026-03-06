import os


class BlacklistManager:

    def __init__(self, path="logs/blacklist.txt"):

        self.path = path
        self.blacklist = set()

        os.makedirs("logs", exist_ok=True)

        # Load existing blacklist
        if os.path.exists(self.path):
            try:
                with open(self.path, "r") as f:
                    for line in f:
                        ip = line.strip()
                        if ip:
                            self.blacklist.add(ip)
            except Exception:
                pass

    # ----------------------------------
    # Add IP to blacklist
    # ----------------------------------
    def add_ip(self, ip):

        if ip in self.blacklist:
            return

        self.blacklist.add(ip)

        try:
            with open(self.path, "a") as f:
                f.write(ip + "\n")
        except Exception:
            pass

        print(f"🚫 IP BLACKLISTED: {ip}")

    # ----------------------------------
    # Compatibility method (prevents crash)
    # ----------------------------------
    def add(self, ip):
        self.add_ip(ip)

    # ----------------------------------
    # Check if IP is blacklisted
    # ----------------------------------
    def is_blacklisted(self, ip):

        return ip in self.blacklist

    # ----------------------------------
    # Remove IP from blacklist
    # ----------------------------------
    def remove_ip(self, ip):

        if ip not in self.blacklist:
            return

        self.blacklist.remove(ip)

        try:
            with open(self.path, "w") as f:
                for ip_addr in self.blacklist:
                    f.write(ip_addr + "\n")
        except Exception:
            pass

        print(f"✅ IP UNBLOCKED: {ip}")