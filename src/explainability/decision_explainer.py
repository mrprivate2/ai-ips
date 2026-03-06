def explain_attack(features, attack_type):

    reasons = []

    try:

        packet_rate = features[0]
        syn_ratio = features[1]
        port_entropy = features[2]

        if packet_rate > 100:
            reasons.append("Packet rate anomaly")

        if syn_ratio > 0.7:
            reasons.append("SYN flood pattern")

        if port_entropy > 3:
            reasons.append("Abnormal port entropy")

    except:
        pass

    if not reasons:
        reasons.append("Suspicious traffic pattern")

    return reasons