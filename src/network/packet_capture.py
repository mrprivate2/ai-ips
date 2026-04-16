from scapy.all import sniff, IP, TCP, UDP
from src.network.feature_mapper import FeatureMapper


class PacketCapture:
    """
    Captures live network traffic and sends
    processed feature vectors to AI-IPS.
    """

    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.mapper = FeatureMapper()

    # -------------------------------------
    # PROCESS PACKET
    # -------------------------------------
    def process_packet(self, packet):

        try:

            if IP not in packet:
                return

            ip_layer = packet[IP]

            # =============================
            # EXTRACT METADATA
            # =============================

            src_ip = ip_layer.src
            dst_ip = ip_layer.dst
            protocol = ip_layer.proto

            src_port = 0
            dst_port = 0
            tcp_flag = ""

            if TCP in packet:
                tcp = packet[TCP]
                src_port = tcp.sport
                dst_port = tcp.dport
                tcp_flag = str(tcp.flags)

            elif UDP in packet:
                udp = packet[UDP]
                src_port = udp.sport
                dst_port = udp.dport

            # =============================
            # FEATURE EXTRACTION
            # =============================

            features = self.mapper.map_packet(packet)

            # =============================
            # METADATA PACKAGE
            # =============================

            metadata = {
                "source_ip": src_ip,
                "destination_ip": dst_ip,
                "protocol": protocol,
                "source_port": src_port,
                "destination_port": dst_port,
                "tcp_flag": tcp_flag
            }

            # =============================
            # SEND TO ENGINE
            # =============================

            self.orchestrator.process(features, metadata)

        except Exception:
            pass  # prevent crash

    # -------------------------------------
    # START SNIFFING
    # -------------------------------------
    def start(self, interface="en0"):

        print(f"[+] Starting AI-IPS Packet Capture on {interface}")

        sniff(
            iface=interface,
            prn=self.process_packet,
            store=False,
            filter="ip"   # 🔥 important (reduces noise)
        )