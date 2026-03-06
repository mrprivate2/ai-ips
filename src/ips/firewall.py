import subprocess


class FirewallManager:

    def __init__(self):

        self.table = "ai_blocklist"

        # cache of blocked IPs to avoid duplicate pfctl calls
        self.blocked_ips = set()

        print("[FIREWALL] Initialized (PF Table Mode)")

    # --------------------------------
    # BLOCK IP
    # --------------------------------
    def block_ip(self, ip):

        # prevent duplicate blocking
        if ip in self.blocked_ips:
            return

        try:

            subprocess.run(
                ["sudo", "pfctl", "-t", self.table, "-T", "add", ip],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False
            )

            self.blocked_ips.add(ip)

            print(f"[FIREWALL] Table Blocked IP: {ip}")

        except Exception as e:
            print("Firewall block error:", e)

    # --------------------------------
    # UNBLOCK IP
    # --------------------------------
    def unblock_ip(self, ip):

        if ip not in self.blocked_ips:
            return

        try:

            subprocess.run(
                ["sudo", "pfctl", "-t", self.table, "-T", "delete", ip],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False
            )

            self.blocked_ips.remove(ip)

            print(f"[FIREWALL] Table Unblocked IP: {ip}")

        except Exception as e:
            print("Firewall unblock error:", e)