import subprocess
import platform
import os

class FirewallManager:

    def __init__(self):
        self.system = platform.system()
        self.table = "ai_blocklist"
        self.blocked_ips = set()

        print(f"[FIREWALL] Initializing for {self.system}...")

        if self.system == "Darwin":
            self.enable_pf()
            self._verify_pf_rule()
        elif self.system == "Linux":
            self._check_iptables()
        else:
            print(f"[FIREWALL] Warning: OS {self.system} not fully supported for automatic blocking.")

        print("[FIREWALL] Ready")

    # =============================
    # MACOS: ENABLE PF
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

    def _verify_pf_rule(self):
        """Checks if the blocking rule for our table exists."""
        try:
            result = subprocess.run(
                ["sudo", "pfctl", "-s", "rules"],
                capture_output=True,
                text=True
            )
            if self.table not in result.stdout:
                print(f"⚠️  [FIREWALL] Warning: No PF rule found for table <{self.table}>.")
                print(f"👉 To enable blocking, add this line to /etc/pf.conf:")
                print(f"   block drop in from <{self.table}> to any")
                print(f"   Then run: sudo pfctl -f /etc/pf.conf")
        except:
            pass

    # =============================
    # LINUX: IPTABLES CHECK
    # =============================
    def _check_iptables(self):
        try:
            subprocess.run(["sudo", "iptables", "-L"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            print("⚠️  [FIREWALL] Warning: iptables not accessible. Automatic blocking may fail.")

    # =============================
    # BLOCK IP
    # =============================

    def block_ip(self, ip):
        if not ip or ip in self.blocked_ips:
            return

        try:
            if self.system == "Darwin":
                subprocess.run(
                    ["sudo", "pfctl", "-t", self.table, "-T", "add", ip],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            elif self.system == "Linux":
                subprocess.run(
                    ["sudo", "iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            
            self.blocked_ips.add(ip)
            print(f"🚫 [FIREWALL] Blocked IP: {ip}")

        except Exception as e:
            print(f"[FIREWALL] Block error for {ip}:", e)

    # =============================
    # UNBLOCK IP
    # =============================

    def unblock_ip(self, ip):
        if ip not in self.blocked_ips:
            return

        try:
            if self.system == "Darwin":
                subprocess.run(
                    ["sudo", "pfctl", "-t", self.table, "-T", "delete", ip],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            elif self.system == "Linux":
                subprocess.run(
                    ["sudo", "iptables", "-D", "INPUT", "-s", ip, "-j", "DROP"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

            self.blocked_ips.remove(ip)
            print(f"✅ [FIREWALL] Unblocked IP: {ip}")

        except Exception as e:
            print(f"[FIREWALL] Unblock error for {ip}:", e)

    # =============================
    # SHOW BLOCKED IPS
    # =============================

    def show_blocked(self):
        try:
            if self.system == "Darwin":
                result = subprocess.run(
                    ["sudo", "pfctl", "-t", self.table, "-T", "show"],
                    capture_output=True,
                    text=True
                )
                print(f"\n[FIREWALL TABLE: {self.table}]\n")
                print(result.stdout)
            elif self.system == "Linux":
                result = subprocess.run(
                    ["sudo", "iptables", "-L", "INPUT", "-v", "-n"],
                    capture_output=True,
                    text=True
                )
                print("\n[IPTABLES INPUT RULES]\n")
                print(result.stdout)

        except Exception as e:
            print("[FIREWALL] Show error:", e)
