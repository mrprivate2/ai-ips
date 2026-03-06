from scapy.all import sniff, IP
from src.network.feature_mapper import FeatureMapper


class PacketCapture:
    """
    Captures live network traffic and sends
    processed feature vectors to AI-IPS.
    """

    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.mapper = FeatureMapper()

    def process_packet(self, packet):

        if IP not in packet:
            return

        features = self.mapper.map_packet(packet)

        metadata = {
            "source_ip": packet[IP].src,
            "destination_ip": packet[IP].dst,
            "protocol": packet[IP].proto
        }

        self.orchestrator.process(features, metadata)

    def start(self, interface="en0"):
        print(f"[+] Starting AI-IPS Packet Capture on {interface}")
        sniff(iface=interface, prn=self.process_packet, store=False)