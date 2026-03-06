import numpy as np
from scapy.layers.inet import IP, TCP, UDP


class FeatureMapper:
    """
    Converts raw packets into feature vectors
    compatible with trained ML model.
    """

    def __init__(self, feature_size=41):
        self.feature_size = feature_size

    def map_packet(self, packet):

        features = np.zeros((1, self.feature_size))

        if IP in packet:
            features[0][0] = len(packet)
            features[0][1] = packet[IP].ttl
            features[0][2] = packet[IP].proto

        if TCP in packet:
            features[0][3] = packet[TCP].sport
            features[0][4] = packet[TCP].dport
            features[0][5] = int(packet[TCP].flags)

        if UDP in packet:
            features[0][6] = packet[UDP].sport
            features[0][7] = packet[UDP].dport

        return features