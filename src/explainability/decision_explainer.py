# =========================================
# AI-IPS Explainability Module
# =========================================

"""
Standalone explainability module
NO circular imports
"""

from src.explainability.feature_importance import explain_features


def explain_attack(features, attack_type):
    """
    Generate explanation for detected attack
    """

    try:

        # =============================
        # BASE ATTACK EXPLANATION
        # =============================

        explanation_map = {

            "PORT_SCAN": "Multiple ports accessed rapidly",

            "SYN_FLOOD": "High SYN packet rate without proper handshake",

            "TRAFFIC_ANOMALY": "Abnormally high traffic volume detected",

            "ANOMALY_DETECTED": "Unusual behavior detected by anomaly model",

            "NORMAL": "Traffic appears normal"
        }

        base_explanation = explanation_map.get(
            attack_type,
            "Suspicious behavior detected"
        )

        # =============================
        # FEATURE EXPLANATION
        # =============================

        feature_reasons = explain_features(features)

        # =============================
        # COMBINE OUTPUT
        # =============================

        if feature_reasons:
            full_explanation = base_explanation + " | " + " | ".join(feature_reasons)
        else:
            full_explanation = base_explanation

        return full_explanation

    except Exception as e:
        return f"Explanation error: {str(e)}"