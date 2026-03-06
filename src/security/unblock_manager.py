import time
from threading import Thread


class UnblockManager:

    def __init__(self, firewall_manager, blacklist_manager, duration=300):

        self.firewall_manager = firewall_manager
        self.blacklist_manager = blacklist_manager

        # unblock duration (seconds)
        self.duration = duration

        # track active timers
        self.active_blocks = {}

    # ----------------------------------
    # BLOCK WITH TIMER
    # ----------------------------------
    def block_with_timer(self, ip):

        # prevent duplicate timers
        if ip in self.active_blocks:
            return

        # block immediately
        self.firewall_manager.block_ip(ip)
        self.blacklist_manager.add_ip(ip)

        # start timer thread
        t = Thread(target=self._timer, args=(ip,), daemon=True)

        self.active_blocks[ip] = t

        t.start()

    # ----------------------------------
    # TIMER
    # ----------------------------------
    def _timer(self, ip):

        try:

            time.sleep(self.duration)

            self.firewall_manager.unblock_ip(ip)

            self.blacklist_manager.remove_ip(ip)

            print(f"[AUTO-UNBLOCKED] {ip}")

        except Exception as e:

            print("Unblock error:", e)

        finally:

            # cleanup
            if ip in self.active_blocks:
                del self.active_blocks[ip]