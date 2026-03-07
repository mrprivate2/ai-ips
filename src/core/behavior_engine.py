import time
from collections import defaultdict


class BehaviorEngine:

    def __init__(self):

        # packet timestamps per IP
        self.ip_packet_times = defaultdict(list)

        # unique ports accessed per IP
        self.ip_ports = defaultdict(set)

        # SYN packet counter
        self.syn_counts = defaultdict(int)

        # cleanup timer
        self.last_cleanup = time.time()

        # detection window (shorter = faster detection)
        self.window_seconds = 3

    # ---------------------------------------
    # ANALYZE NETWORK BEHAVIOR
    # ---------------------------------------

    def analyze(self, source_ip, destination_port, tcp_flag):

        now = time.time()

        try:
            destination_port = int(destination_port)
        except Exception:
            destination_port = 0

        tcp_flag = str(tcp_flag)

        # -----------------------------
        # Track packet timestamps
        # -----------------------------

        self.ip_packet_times[source_ip].append(now)

        # keep only recent packets
        self.ip_packet_times[source_ip] = [
            t for t in self.ip_packet_times[source_ip]
            if now - t <= self.window_seconds
        ]

        # -----------------------------
        # Track accessed ports
        # -----------------------------

        self.ip_ports[source_ip].add(destination_port)

        # -----------------------------
        # Track SYN packets
        # -----------------------------

        # SYN without ACK = connection attempt
        if "S" in tcp_flag and "A" not in tcp_flag:
            self.syn_counts[source_ip] += 1

        # -----------------------------
        # Compute metrics
        # -----------------------------

        packet_rate = len(self.ip_packet_times[source_ip])
        port_count = len(self.ip_ports[source_ip])
        syn_count = self.syn_counts[source_ip]

        risk = 0.0
        attack_type = "NORMAL"

        # -----------------------------
        # FAST PORT SCAN detection
        # -----------------------------
        # Nmap sends many SYN packets quickly

        if syn_count >= 15:
            risk = 0.95
            attack_type = "PORT_SCAN"

        # backup rule if ports vary
        elif port_count >= 8:
            risk = 0.95
            attack_type = "PORT_SCAN"

        # -----------------------------
        # SYN FLOOD detection
        # -----------------------------

        elif syn_count >= 60:
            risk = 0.95
            attack_type = "SYN_FLOOD"

        # -----------------------------
        # TRAFFIC ANOMALY detection
        # -----------------------------

        elif packet_rate >= 40:
            risk = 0.80
            attack_type = "TRAFFIC_ANOMALY"

        # -----------------------------
        # Periodic memory cleanup
        # -----------------------------

        if now - self.last_cleanup > 60:

            for ip in list(self.ip_packet_times.keys()):

                if not self.ip_packet_times[ip] or now - self.ip_packet_times[ip][-1] > 60:

                    self.ip_packet_times.pop(ip, None)
                    self.ip_ports.pop(ip, None)
                    self.syn_counts.pop(ip, None)

            self.last_cleanup = now

        # -----------------------------
        # Return result
        # -----------------------------

        return {
            "risk": min(risk, 1.0),
            "attack_type": attack_type
        }