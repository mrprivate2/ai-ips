from scapy.all import sniff, IP, TCP
import numpy as np


class PacketSniffer:

    def __init__(self, interface="en0"):

        self.interface = interface
        print(f"[SNIFFER] Listening on interface: {self.interface}")

    # ---------------------------------------
    # START CAPTURE
    # ---------------------------------------

    def capture(self, packet_callback):

        sniff(
            iface=self.interface,
            prn=lambda pkt: self.process_packet(pkt, packet_callback),
            store=False
        )

    # ---------------------------------------
    # PROCESS PACKET
    # ---------------------------------------

    def process_packet(self, packet, callback):

        try:

            if not packet.haslayer(IP):
                return

            ip_layer = packet[IP]

            src_ip = ip_layer.src
            dst_ip = ip_layer.dst

            dst_port = 0
            tcp_flag = ""

            # ----------------------------
            # TCP extraction
            # ----------------------------

            if packet.haslayer(TCP):

                tcp = packet[TCP]

                dst_port = int(tcp.dport)

                flags = str(tcp.flags)

                # detect SYN (scan attempts)
                if "S" in flags and "A" not in flags:
                    tcp_flag = "S"

                # SYN+ACK
                elif "S" in flags and "A" in flags:
                    tcp_flag = "SA"

                # ACK
                elif "A" in flags:
                    tcp_flag = "A"

                # FIN
                elif "F" in flags:
                    tcp_flag = "F"

            # ----------------------------
            # Feature extraction
            # ----------------------------

            packet_len = len(packet)

            features = np.array([
                packet_len,
                dst_port
            ])

            # ----------------------------
            # Send to IPS engine
            # ----------------------------

            callback(
                features,
                src_ip,
                dst_ip,
                dst_port,
                tcp_flag
            )

        except Exception:
            # IPS must never crash due to packet parsing
            pass