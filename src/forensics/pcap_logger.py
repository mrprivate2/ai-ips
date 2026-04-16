from scapy.all import wrpcap
import os
import time
from collections import defaultdict


class PCAPLogger:

    def __init__(self):

        self.dir = "logs/pcap"
        os.makedirs(self.dir, exist_ok=True)

        # 🧠 buffer packets per IP
        self.packet_buffer = defaultdict(list)

        # save after N packets
        self.buffer_limit = 5

    # =============================
    # SAVE PACKET (BUFFERED)
    # =============================

    def save_packet(self, packet, src_ip, attack_type="NORMAL"):

        try:

            # only log suspicious traffic
            if attack_type == "NORMAL":
                return

            # sanitize IP for filename
            safe_ip = src_ip.replace(".", "_")

            # add to buffer
            self.packet_buffer[safe_ip].append(packet)

            # save when buffer full
            if len(self.packet_buffer[safe_ip]) >= self.buffer_limit:

                filename = f"{self.dir}/attack_{safe_ip}_{int(time.time())}.pcap"

                wrpcap(filename, self.packet_buffer[safe_ip])

                print(f"[PCAP] Saved {len(self.packet_buffer[safe_ip])} packets → {filename}")

                # clear buffer
                self.packet_buffer[safe_ip] = []

        except Exception as e:
            print("[PCAP ERROR]", e)