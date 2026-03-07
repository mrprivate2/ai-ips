import joblib
import numpy as np
import os
import warnings

# hide sklearn warnings
warnings.filterwarnings("ignore")


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
        # MODEL PATHS
        # ---------------------------

        self.supervised_model_path = supervised_model_path
        self.unsupervised_model_path = unsupervised_model_path
        self.scaler_path = config.get("scaler_path", "src/models/saved/scaler.pkl")

        self.supervised_model = None
        self.unsupervised_model = None
        self.scaler = None

        # ---------------------------
        # LOAD SUPERVISED MODEL
        # ---------------------------

        if os.path.exists(self.supervised_model_path):
            try:
                self.supervised_model = joblib.load(self.supervised_model_path)
                print("[AI] Supervised model loaded")
            except Exception as e:
                print("[AI] Failed to load supervised model:", e)
        else:
            print("[AI] Supervised model not found")

        # ---------------------------
        # LOAD ANOMALY MODEL
        # ---------------------------

        if os.path.exists(self.unsupervised_model_path):
            try:
                self.unsupervised_model = joblib.load(self.unsupervised_model_path)
                print("[AI] Anomaly model loaded")
            except Exception as e:
                print("[AI] Failed to load anomaly model:", e)
        else:
            print("[AI] Anomaly model disabled")

        # ---------------------------
        # LOAD SCALER
        # ---------------------------

        if os.path.exists(self.scaler_path):
            try:
                self.scaler = joblib.load(self.scaler_path)
                print("[AI] Scaler loaded")
            except Exception as e:
                print("[AI] Failed to load scaler:", e)
        else:
            print("[AI] Scaler disabled")

    # -------------------------------------
    # MAIN DETECTION FUNCTION
    # -------------------------------------

    def detect(self, X):

        try:

            if X is None:
                return self._safe_result()

            X = np.array(X, dtype=float)

            if X.ndim == 1:
                X = X.reshape(1, -1)

            # ---------------------------
            # SCALE FEATURES
            # ---------------------------

            try:
                if self.scaler is not None:
                    X_scaled = self.scaler.transform(X)
                else:
                    X_scaled = X
            except Exception:
                X_scaled = X

            # ---------------------------
            # SUPERVISED MODEL
            # ---------------------------

            supervised_score = 0.0
            predicted_class = 0

            if self.supervised_model is not None:

                try:

                    if hasattr(self.supervised_model, "predict_proba"):

                        probs = self.supervised_model.predict_proba(X_scaled)

                        if probs.shape[1] > 1:
                            supervised_score = float(probs[0][1])
                        else:
                            supervised_score = float(probs[0][0])

                        predicted_class = int(np.argmax(probs))

                    else:

                        pred = self.supervised_model.predict(X_scaled)[0]
                        predicted_class = int(pred)
                        supervised_score = float(pred)

                except Exception:
                    pass

            # ---------------------------
            # ANOMALY MODEL
            # ---------------------------

            anomaly_score = 0.0

            if self.unsupervised_model is not None:

                try:

                    raw_score = float(
                        self.unsupervised_model.decision_function(X_scaled)[0]
                    )

                    anomaly_score = max(0.0, -raw_score)
                    anomaly_score = min(anomaly_score, 1.0)

                except Exception:
                    anomaly_score = 0.0

            # ---------------------------
            # HYBRID SCORE
            # ---------------------------

            final_threat_score = (
                self.weight_supervised * supervised_score
                + self.weight_anomaly * anomaly_score
            )

            # ---------------------------
            # ZERO DAY DETECTION
            # ---------------------------

            zero_day_detected = False

            if anomaly_score >= self.zero_day_threshold:
                zero_day_detected = True
                final_threat_score = min(final_threat_score + 0.2, 1.0)

            # ---------------------------
            # THREAT LEVEL
            # ---------------------------

            if final_threat_score >= self.block_threshold:
                threat_level = "BLOCK"

            elif final_threat_score >= self.warning_threshold:
                threat_level = "WARNING"

            else:
                threat_level = "NORMAL"

            confidence = abs(supervised_score - 0.5) * 2

            return {
                "predicted_class_index": predicted_class,
                "supervised_score": float(supervised_score),
                "anomaly_score": float(anomaly_score),
                "final_threat_score": float(final_threat_score),
                "confidence": float(confidence),
                "threat_level": threat_level,
                "zero_day": zero_day_detected,
                "explanation_flags": {}
            }

        except Exception as e:

            print("[AI] Detection error:", e)

            return self._safe_result()

    # -------------------------------------
    # SAFE DEFAULT RESULT
    # -------------------------------------

    def _safe_result(self):

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