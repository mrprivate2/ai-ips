import numpy as np


# =========================================
# FEATURE IMPORTANCE ENGINE
# =========================================

def get_feature_importance(features):
    """
    Analyze feature vector and return important indicators

    Args:
        features (list or np.array)

    Returns:
        dict: important features + scores
    """

    if features is None:
        return {}

    try:

        features = np.array(features, dtype=float)

        importance = {}

        # =============================
        # MAPPED HEURISTICS (matching sniffer.py)
        # =============================
        # 0: packet_len_norm
        # 1: port_norm
        # 2: ttl_norm
        # 3: protocol_norm
        # 4: flag_norm
        # 5: time_norm
        # 6: burst
        # 7: port_risk
        # 8: is_external

        if len(features) > 0:
            importance["packet_length"] = float(features[0])

        if len(features) > 1:
            importance["destination_port"] = float(features[1])

        if len(features) > 5:
            importance["inter_arrival_time"] = float(features[5])

        if len(features) > 7:
            importance["port_risk"] = float(features[7])

        # =============================
        # TOP FEATURES
        # =============================

        top_indices = np.argsort(features)[-3:][::-1]

        importance["top_features"] = [
            {"index": int(i), "value": float(features[i])}
            for i in top_indices
        ]

        return importance

    except:
        return {}


# =========================================
# HUMAN READABLE EXPLANATION
# =========================================

def explain_features(features):
    """
    Convert features into readable explanation based on sniffer.py vector:
    [packet_len, port, ttl, protocol, flag, time_diff, burst, port_risk, is_external]
    """

    reasons = []

    if features is None:
        return reasons

    try:

        # f0: packet_len_norm
        if len(features) > 0 and features[0] > 0.8:
            reasons.append("Abnormally large packet size")

        # f1: port_norm (not very useful for reason alone without port_risk)
        
        # f2: ttl_norm
        if len(features) > 2 and (features[2] < 0.2 or features[2] > 0.9):
            reasons.append("Suspicious TTL value")

        # f4: flag_norm
        if len(features) > 4 and features[4] < 0.2: # Likely SYN
            reasons.append("Connection request (SYN) spike")

        # f5: time_norm (inter-arrival time)
        if len(features) > 5 and features[5] < 0.05:
            reasons.append("High-frequency traffic burst")

        # f6: burst
        if len(features) > 6 and features[6] == 1:
            reasons.append("Packet burst detected")

        # f7: port_risk
        if len(features) > 7 and features[7] > 0.7:
            reasons.append("Accessing high-risk/uncommon port")

        # f8: is_external
        if len(features) > 8 and features[8] == 1:
            reasons.append("External source IP")

        if not reasons:
            reasons.append("Heuristic check: No obvious flags (AI model detection only)")

        return reasons

    except:
        return ["Feature analysis failed"]
