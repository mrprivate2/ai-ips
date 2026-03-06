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
            store=False,
            filter="ip"
        )

    # ---------------------------------------
    # PROCESS PACKET
    # ---------------------------------------

    def process_packet(self, packet, callback):

        try:

            # Ignore packets without IP
            if not packet.haslayer(IP):
                return

            ip_layer = packet[IP]

            src_ip = ip_layer.src
            dst_ip = ip_layer.dst

            dst_port = 0
            tcp_flag = ""

            # ----------------------------
            # TCP Extraction
            # ----------------------------

            if packet.haslayer(TCP):

                tcp_layer = packet[TCP]

                dst_port = int(tcp_layer.dport)

                flags = tcp_layer.flags

                if flags & 0x02:
                    tcp_flag = "S"   # SYN
                elif flags & 0x10:
                    tcp_flag = "A"   # ACK
                elif flags & 0x01:
                    tcp_flag = "F"   # FIN
                else:
                    tcp_flag = ""

            # ----------------------------
            # FEATURE EXTRACTION
            # ----------------------------

            packet_len = len(packet)

            # Zero-Day detection needs richer features
            features = np.array([
                packet_len,
                dst_port
            ])

            # ----------------------------
            # SEND TO IPS ENGINE
            # ----------------------------

            callback(
                packet,        # needed for PCAP logging
                features,
                src_ip,
                dst_ip,
                dst_port,
                tcp_flag
            )

        except Exception:

            # IPS must never crash
            pass