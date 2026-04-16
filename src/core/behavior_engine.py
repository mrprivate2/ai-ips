import time
from collections import defaultdict


class BehaviorEngine:

    def __init__(self):

        self.ip_packet_times = defaultdict(list)
        self.ip_ports = defaultdict(set)
        self.syn_counts = defaultdict(int)
        self.last_seen = {}
        self.ip_history = defaultdict(int)

        self.last_cleanup = time.time()
        self.window_seconds = 5  # improved detection window

    # ---------------------------------------
    # ANALYZE NETWORK BEHAVIOR
    # ---------------------------------------

    def analyze(self, source_ip, destination_port, tcp_flag):

        now = time.time()

        try:
            destination_port = int(destination_port)
        except:
            destination_port = 0

        tcp_flag = str(tcp_flag)

        # -----------------------------
        # TRACK TIMESTAMPS
        # -----------------------------

        self.ip_packet_times[source_ip].append(now)

        self.ip_packet_times[source_ip] = [
            t for t in self.ip_packet_times[source_ip]
            if now - t <= self.window_seconds
        ]

        # -----------------------------
        # TRACK PORTS
        # -----------------------------

        self.ip_ports[source_ip].add(destination_port)

        # -----------------------------
        # TRACK SYN
        # -----------------------------

        if "S" in tcp_flag and "A" not in tcp_flag:
            self.syn_counts[source_ip] += 1

        # -----------------------------
        # INTER-ARRIVAL TIME
        # -----------------------------

        time_diff = now - self.last_seen.get(source_ip, now)
        self.last_seen[source_ip] = now

        # -----------------------------
        # METRICS
        # -----------------------------

        packet_rate = len(self.ip_packet_times[source_ip])
        port_count = len(self.ip_ports[source_ip])
        syn_count = self.syn_counts[source_ip]

        risk = 0.0
        attack_type = "NORMAL"

        # =============================
        # 🔥 PORT SCAN
        # =============================

        if port_count >= 8 and packet_rate > 10:
            risk = 0.9
            attack_type = "PORT_SCAN"

        # =============================
        # 🔥 SYN FLOOD
        # =============================

        elif syn_count >= 30:
            risk = 0.95
            attack_type = "SYN_FLOOD"

        # =============================
        # 🔥 TRAFFIC BURST
        # =============================

        elif packet_rate >= 25:
            risk = 0.75
            attack_type = "TRAFFIC_BURST"

        # =============================
        # 🔥 STEALTH ATTACK
        # =============================

        elif time_diff < 0.03 and packet_rate > 10:
            risk = 0.65
            attack_type = "STEALTH_ATTACK"

        # =============================
        # HISTORY BOOST
        # =============================

        if attack_type != "NORMAL":
            self.ip_history[source_ip] += 1

        if self.ip_history[source_ip] > 2:
            risk += 0.1

        risk = min(risk, 1.0)

        # -----------------------------
        # CLEANUP (memory safe)
        # -----------------------------

        if now - self.last_cleanup > 60:

            for ip in list(self.ip_packet_times.keys()):

                if not self.ip_packet_times[ip] or now - self.ip_packet_times[ip][-1] > 60:

                    self.ip_packet_times.pop(ip, None)
                    self.ip_ports.pop(ip, None)
                    self.syn_counts.pop(ip, None)
                    self.last_seen.pop(ip, None)
                    self.ip_history.pop(ip, None)

            self.last_cleanup = now

        return {
            "risk": risk,
            "attack_type": attack_type
        }