import joblib
import numpy as np
import os


class HybridDetector:

    def __init__(self, supervised_model_path, unsupervised_model_path, config):

        # ---------------------------
        # CONFIG
        # ---------------------------

        self.weight_supervised = config.get("weight_supervised", 0.7)
        self.weight_anomaly = config.get("weight_anomaly", 0.3)

        self.warning_threshold = config.get("warning_threshold", 0.4)
        self.block_threshold = config.get("block_threshold", 0.6)

        self.zero_day_threshold = config.get("zero_day_threshold", 0.8)

        # ---------------------------
        # LOAD MODELS SAFELY
        # ---------------------------

        try:
            self.supervised_model = joblib.load(supervised_model_path)
        except Exception:
            print("[AI] Failed to load supervised model")
            self.supervised_model = None

        try:
            self.unsupervised_model = joblib.load(unsupervised_model_path)
        except Exception:
            print("[AI] Failed to load anomaly model")
            self.unsupervised_model = None

        # ---------------------------
        # LOAD SCALER
        # ---------------------------

        scaler_path = os.path.join(
            os.path.dirname(__file__),
            "../models/saved/scaler.pkl"
        )

        try:
            self.scaler = joblib.load(scaler_path)
        except Exception:
            print("[AI] Failed to load scaler")
            self.scaler = None

    # -------------------------------------
    # MAIN DETECTION FUNCTION
    # -------------------------------------

    def detect(self, X: np.ndarray):

        try:

            if X is None:
                raise ValueError("Empty feature vector")

            if len(X.shape) == 1:
                X = X.reshape(1, -1)

            # ---------------------------
            # SCALE FEATURES
            # ---------------------------

            if self.scaler is not None:
                X_scaled = self.scaler.transform(X)
            else:
                X_scaled = X

            # ---------------------------
            # SUPERVISED DETECTION
            # ---------------------------

            supervised_score = 0.0
            predicted_class = 0

            if self.supervised_model is not None:

                probs = self.supervised_model.predict_proba(X_scaled)

                supervised_score = float(probs[0][1])
                predicted_class = int(np.argmax(probs))

            # ---------------------------
            # UNSUPERVISED ANOMALY
            # ---------------------------

            anomaly_score = 0.0

            if self.unsupervised_model is not None:

                raw_score = float(
                    self.unsupervised_model.decision_function(X_scaled)[0]
                )

                # convert anomaly score to 0-1 scale
                anomaly_score = max(0.0, -raw_score)

                anomaly_score = min(anomaly_score, 1.0)

            # ---------------------------
            # HYBRID FUSION
            # ---------------------------

            final_threat_score = (
                self.weight_supervised * supervised_score
                + self.weight_anomaly * anomaly_score
            )

            # ---------------------------
            # ZERO-DAY DETECTION
            # ---------------------------

            zero_day_detected = False

            if anomaly_score >= self.zero_day_threshold:

                zero_day_detected = True

                final_threat_score = min(
                    final_threat_score + 0.2,
                    1.0
                )

            # ---------------------------
            # THREAT LEVEL
            # ---------------------------

            if final_threat_score >= self.block_threshold:

                threat_level = "BLOCK"

            elif final_threat_score >= self.warning_threshold:

                threat_level = "WARNING"

            else:

                threat_level = "NORMAL"

            # ---------------------------
            # CONFIDENCE
            # ---------------------------

            confidence = abs(supervised_score - 0.5) * 2

            # ---------------------------
            # EXPLANATION FLAGS
            # ---------------------------

            explanation_flags = {

                "high_supervised_score": supervised_score > 0.7,
                "high_anomaly_score": anomaly_score > 0.6,
                "zero_day_detected": zero_day_detected

            }

            return {

                "predicted_class_index": predicted_class,
                "supervised_score": supervised_score,
                "anomaly_score": anomaly_score,
                "final_threat_score": float(final_threat_score),
                "confidence": float(confidence),
                "threat_level": threat_level,
                "zero_day": zero_day_detected,
                "explanation_flags": explanation_flags

            }

        except Exception as e:

            print("[AI] Detection error:", e)

            return {

                "predicted_class_index": 0,
                "supervised_score": 0.0,
                "anomaly_score": 0.0,
                "final_threat_score": 0.0,
                "confidence": 0.0,
                "threat_level": "NORMAL",
                "zero_day": False,
                "explanation_flags": {}

            }