import time
from collections import defaultdict


class BehaviorEngine:

    def __init__(self):

        # packet timestamps per IP
        self.ip_packet_times = defaultdict(list)

        # ports accessed per IP
        self.ip_ports = defaultdict(set)

        # SYN packet counts
        self.syn_counts = defaultdict(int)

        # last cleanup time
        self.last_cleanup = time.time()

    def analyze(self, source_ip, destination_port, tcp_flag):

        now = time.time()

        # -----------------------------
        # Track packet timestamps
        # -----------------------------
        self.ip_packet_times[source_ip].append(now)

        # Keep only last 5 seconds
        self.ip_packet_times[source_ip] = [
            t for t in self.ip_packet_times[source_ip]
            if now - t <= 5
        ]

        # -----------------------------
        # Track ports accessed
        # -----------------------------
        self.ip_ports[source_ip].add(destination_port)

        # -----------------------------
        # Track SYN packets
        # -----------------------------
        if tcp_flag == "S":
            self.syn_counts[source_ip] += 1

        # -----------------------------
        # Metrics
        # -----------------------------
        packet_rate = len(self.ip_packet_times[source_ip])
        port_count = len(self.ip_ports[source_ip])
        syn_count = self.syn_counts[source_ip]

        risk = 0.0
        attack_type = "NORMAL"

        # -----------------------------
        # PORT SCAN detection
        # -----------------------------
        if port_count > 40:
            risk = 0.9
            attack_type = "PORT_SCAN"

        # -----------------------------
        # SYN FLOOD detection
        # -----------------------------
        elif syn_count > 300:
            risk = 0.95
            attack_type = "SYN_FLOOD"

        # -----------------------------
        # TRAFFIC BURST detection
        # -----------------------------
        elif packet_rate > 150:
            risk = 0.75
            attack_type = "TRAFFIC_ANOMALY"

        # -----------------------------
        # Periodic memory cleanup
        # -----------------------------
        if now - self.last_cleanup > 60:

            for ip in list(self.ip_packet_times.keys()):

                if len(self.ip_packet_times[ip]) == 0:
                    self.ip_packet_times.pop(ip, None)
                    self.ip_ports.pop(ip, None)
                    self.syn_counts.pop(ip, None)

            self.last_cleanup = now

        return {
            "risk": min(risk, 1.0),
            "attack_type": attack_type
        }