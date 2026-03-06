from scapy.all import wrpcap
import os
import time


class PCAPLogger:

    def __init__(self):

        self.dir = "logs/pcap"

        os.makedirs(self.dir, exist_ok=True)

    def save_packet(self, packet, src_ip):

        try:

            filename = f"{self.dir}/attack_{src_ip}_{int(time.time())}.pcap"

            wrpcap(filename, [packet])

            print(f"[PCAP] Packet saved: {filename}")

        except Exception as e:

            print("PCAP save error:", e)