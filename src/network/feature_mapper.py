import numpy as np
from scapy.layers.inet import IP, TCP, UDP


class FeatureMapper:
    """
    Converts raw packets into ML-ready feature vectors
    """

    def __init__(self, feature_size=41):
        self.feature_size = feature_size

    def map_packet(self, packet):

        features = np.zeros(self.feature_size)

        try:

            # =============================
            # BASIC IP FEATURES
            # =============================

            if IP in packet:

                ip_layer = packet[IP]

                features[0] = min(len(packet) / 1500, 1.0)  # normalized size
                features[1] = ip_layer.ttl / 255
                features[2] = ip_layer.proto / 255

            # =============================
            # TCP FEATURES
            # =============================

            if TCP in packet:

                tcp = packet[TCP]

                features[3] = tcp.sport / 65535
                features[4] = tcp.dport / 65535

                # flag-based features
                flags = tcp.flags

                features[5] = int("S" in str(flags))  # SYN
                features[6] = int("A" in str(flags))  # ACK
                features[7] = int("F" in str(flags))  # FIN
                features[8] = int("R" in str(flags))  # RST

                # SYN without ACK → suspicious
                features[9] = 1 if ("S" in str(flags) and "A" not in str(flags)) else 0

            # =============================
            # UDP FEATURES
            # =============================

            if UDP in packet:

                udp = packet[UDP]

                features[10] = udp.sport / 65535
                features[11] = udp.dport / 65535

            # =============================
            # SIMPLE BEHAVIOR SIGNALS
            # =============================

            features[12] = 1 if len(packet) > 1000 else 0  # large packet
            features[13] = 1 if len(packet) < 100 else 0   # tiny packet

            # =============================
            # FILL REMAINING FEATURES
            # =============================

            # keep rest as 0 (model trained like this)

        except Exception:
            pass

        return features.reshape(1, -1)