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
        # BASIC HEURISTICS
        # =============================

        # Feature 0 → traffic intensity
        if len(features) > 0:
            importance["traffic_intensity"] = float(features[0])

        # Feature 1 → connection rate
        if len(features) > 1:
            importance["connection_rate"] = float(features[1])

        # Feature 2 → irregular behavior
        if len(features) > 2:
            importance["pattern_irregularity"] = float(features[2])

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
    Convert features into readable explanation
    """

    reasons = []

    if features is None:
        return reasons

    try:

        if len(features) > 0 and features[0] > 0.8:
            reasons.append("High traffic intensity")

        if len(features) > 1 and features[1] > 0.7:
            reasons.append("Excessive connection attempts")

        if len(features) > 2 and 0.3 < features[2] < 0.8:
            reasons.append("Irregular traffic pattern")

        if len(features) > 3 and features[3] > 0.85:
            reasons.append("Abnormal packet distribution")

        if not reasons:
            reasons.append("No strong anomaly indicators")

        return reasons

    except:
        return ["Feature analysis failed"]