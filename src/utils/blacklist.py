import os


class BlacklistManager:
    """
    Manages blacklisted IP addresses.
    """

    def __init__(self, file_path="logs/blacklist.txt"):
        self.file_path = file_path

        # Ensure logs directory exists
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

        # Create file if not exists
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as f:
                pass

    # -----------------------------
    # Add IP to blacklist
    # -----------------------------
    def add_ip(self, ip):
        if not self.is_blacklisted(ip):
            with open(self.file_path, "a") as f:
                f.write(ip + "\n")

    # -----------------------------
    # Check if IP is blacklisted
    # -----------------------------
    def is_blacklisted(self, ip):
        with open(self.file_path, "r") as f:
            return ip in [line.strip() for line in f.readlines()]