from scapy.all import sniff, IP, TCP, UDP, ICMP
import numpy as np
import time
import ipaddress


# ---------------------------------------
# HELPER: PRIVATE IP CHECK
# ---------------------------------------

def is_private_ip(ip):
    try:
        return ipaddress.ip_address(ip).is_private
    except:
        return False


# ---------------------------------------
# PACKET SNIFFER CLASS
# ---------------------------------------

class PacketSniffer:

    def __init__(self, interface="en0"):
        self.interface = interface
        self.last_seen = {}  # track inter-arrival time per IP

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
    # PROCESS PACKET (FINAL 🔥)
    # ---------------------------------------

    def process_packet(self, packet, callback):

        try:

            if not packet.haslayer(IP):
                return

            ip_layer = packet[IP]

            src_ip = ip_layer.src
            dst_ip = ip_layer.dst

            # ----------------------------
            # BASIC FEATURES
            # ----------------------------

            packet_len = len(packet)
            ttl = int(ip_layer.ttl)

            now = time.time()

            if src_ip in self.last_seen:
                time_diff = now - self.last_seen[src_ip]
            else:
                time_diff = 0.0

            self.last_seen[src_ip] = now

            # ----------------------------
            # PROTOCOL + FLAGS
            # ----------------------------

            dst_port = 0
            protocol = 0
            flag_val = 0

            if packet.haslayer(TCP):
                tcp = packet[TCP]
                protocol = 1
                dst_port = int(tcp.dport)

                flags = str(tcp.flags)

                if "S" in flags and "A" not in flags:
                    flag_val = 1
                elif "S" in flags and "A" in flags:
                    flag_val = 2
                elif "A" in flags:
                    flag_val = 3
                elif "F" in flags:
                    flag_val = 4

            elif packet.haslayer(UDP):
                udp = packet[UDP]
                protocol = 2
                dst_port = int(udp.dport)
                flag_val = 5

            elif packet.haslayer(ICMP):
                protocol = 3
                flag_val = 6

            # ----------------------------
            # NORMALIZATION
            # ----------------------------

            packet_len_norm = min(packet_len / 1500, 1.0)
            ttl_norm = ttl / 255
            port_norm = dst_port / 65535
            time_norm = min(time_diff, 1.0)

            protocol_norm = protocol / 3
            flag_norm = flag_val / 6

            # ----------------------------
            # ADVANCED FEATURES
            # ----------------------------

            burst = 1 if time_diff < 0.05 else 0

            well_known_ports = {
                80, 443, 53, 22, 21, 25,
                110, 143, 3306, 3389, 8080
            }

            if dst_port in well_known_ports:
                port_risk = 0
            elif dst_port < 1024:
                port_risk = 0.3
            elif dst_port < 49152:
                port_risk = 0.6
            else:
                port_risk = 1.0

            is_external = 0 if is_private_ip(src_ip) else 1

            # ----------------------------
            # FINAL FEATURE VECTOR
            # ----------------------------

            features = np.array([
                packet_len_norm,
                port_norm,
                ttl_norm,
                protocol_norm,
                flag_norm,
                time_norm,
                burst,
                port_risk,
                is_external
            ])

            # ----------------------------
            # CALLBACK
            # ----------------------------

            callback(
                features,
                src_ip,
                dst_ip,
                dst_port,
                flag_val,
                packet
            )

        except Exception as e:
            print("Sniffer error:", e)