import subprocess


class FirewallManager:

    def __init__(self):

        self.table = "ai_blocklist"
        self.blocked_ips = set()

        print("[FIREWALL] Initializing...")

        self.enable_pf()

        print("[FIREWALL] Ready")

    # =============================
    # ENABLE PF
    # =============================

    def enable_pf(self):

        try:
            subprocess.run(
                ["sudo", "pfctl", "-E"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception as e:
            print("[FIREWALL] PF enable error:", e)

    # =============================
    # BLOCK IP
    # =============================

    def block_ip(self, ip):

        if not ip or ip in self.blocked_ips:
            return

        try:
            subprocess.run(
                ["sudo", "pfctl", "-t", self.table, "-T", "add", ip],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            self.blocked_ips.add(ip)

            print(f"[BLOCKED] {ip}")

        except Exception as e:
            print("[FIREWALL] Block error:", e)

    # =============================
    # UNBLOCK IP (MANUAL ONLY)
    # =============================

    def unblock_ip(self, ip):

        if ip not in self.blocked_ips:
            return

        try:
            subprocess.run(
                ["sudo", "pfctl", "-t", self.table, "-T", "delete", ip],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            self.blocked_ips.remove(ip)

            print(f"[UNBLOCKED] {ip}")

        except Exception as e:
            print("[FIREWALL] Unblock error:", e)

    # =============================
    # SHOW BLOCKED IPS
    # =============================

    def show_blocked(self):

        try:
            result = subprocess.run(
                ["sudo", "pfctl", "-t", self.table, "-T", "show"],
                capture_output=True,
                text=True
            )

            print("\n[FIREWALL TABLE]\n")
            print(result.stdout)

        except Exception as e:
            print("[FIREWALL] Show error:", e)