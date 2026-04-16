import joblib
import numpy as np
import os
import warnings

warnings.filterwarnings("ignore")


class HybridDetector:

    def __init__(self, supervised_model_path, unsupervised_model_path, config):

        self.weight_supervised = config.get("weight_supervised", 0.6)
        self.weight_anomaly = config.get("weight_anomaly", 0.4)

        self.warning_threshold = config.get("warning_threshold", 0.4)
        self.block_threshold = config.get("block_threshold", 0.65)

        # renamed (real meaning)
        self.anomaly_threshold = config.get("anomaly_threshold", 0.6)

        self.supervised_model_path = supervised_model_path
        self.unsupervised_model_path = unsupervised_model_path
        self.scaler_path = config.get("scaler_path", "src/models/saved/scaler.pkl")

        self.supervised_model = None
        self.unsupervised_model = None
        self.scaler = None

        # LOAD MODELS
        self._load_models()

    # -------------------------------------
    # LOAD MODELS
    # -------------------------------------

    def _load_models(self):

        if os.path.exists(self.supervised_model_path):
            try:
                self.supervised_model = joblib.load(self.supervised_model_path)
                print("[AI] Supervised model loaded")
            except Exception as e:
                print("[AI] Failed to load supervised model:", e)

        if os.path.exists(self.unsupervised_model_path):
            try:
                self.unsupervised_model = joblib.load(self.unsupervised_model_path)
                print("[AI] Anomaly model loaded")
            except Exception as e:
                print("[AI] Failed to load anomaly model:", e)

        if os.path.exists(self.scaler_path):
            try:
                self.scaler = joblib.load(self.scaler_path)
                print("[AI] Scaler loaded")
            except Exception as e:
                print("[AI] Failed to load scaler:", e)

    # -------------------------------------
    # MAIN DETECTION
    # -------------------------------------

    def detect(self, X):

        try:

            if X is None:
                return self._safe_result()

            X = np.array(X, dtype=float)

            if X.ndim == 1:
                X = X.reshape(1, -1)

            # SCALE
            try:
                X_scaled = self.scaler.transform(X) if self.scaler else X
            except:
                X_scaled = X

            # =============================
            # SUPERVISED MODEL
            # =============================

            supervised_score = 0.0
            predicted_class = 0

            if self.supervised_model:

                try:
                    if hasattr(self.supervised_model, "predict_proba"):

                        probs = self.supervised_model.predict_proba(X_scaled)
                        supervised_score = float(probs[0][1])
                        predicted_class = int(np.argmax(probs))

                    else:
                        pred = self.supervised_model.predict(X_scaled)[0]
                        supervised_score = float(pred)
                        predicted_class = int(pred)

                except:
                    pass

            # =============================
            # ANOMALY MODEL
            # =============================

            anomaly_score = 0.0

            if self.unsupervised_model:

                try:
                    raw_score = float(self.unsupervised_model.decision_function(X_scaled)[0])

                    # normalize properly
                    anomaly_score = 1 - (raw_score + 0.5)
                    anomaly_score = max(0.0, min(anomaly_score, 1.0))

                except:
                    anomaly_score = 0.0

            # =============================
            # HYBRID SCORE
            # =============================

            final_threat_score = (
                self.weight_supervised * supervised_score +
                self.weight_anomaly * anomaly_score
            )

            # =============================
            # 🧠 ANOMALY DETECTION (REAL)
            # =============================

            attack_type = "NORMAL"

            if anomaly_score >= self.anomaly_threshold:
                attack_type = "ANOMALY_DETECTED"
                final_threat_score = min(final_threat_score + 0.2, 1.0)

            # =============================
            # CONFIDENCE (IMPROVED)
            # =============================

            confidence = (
                abs(supervised_score - anomaly_score)
            )

            # =============================
            # THREAT LEVEL
            # =============================

            if final_threat_score >= self.block_threshold:
                threat_level = "BLOCK"
            elif final_threat_score >= self.warning_threshold:
                threat_level = "WARNING"
            else:
                threat_level = "NORMAL"

            # =============================
            # 🧠 EXPLAINABILITY FLAGS
            # =============================

            explanation_flags = {}

            if supervised_score > 0.7:
                explanation_flags["high_supervised_risk"] = True

            if anomaly_score > 0.7:
                explanation_flags["high_anomaly"] = True

            if abs(supervised_score - anomaly_score) < 0.2:
                explanation_flags["model_agreement"] = True

            return {
                "predicted_class_index": predicted_class,
                "supervised_score": supervised_score,
                "anomaly_score": anomaly_score,
                "final_threat_score": final_threat_score,
                "confidence": confidence,
                "threat_level": threat_level,
                "attack_type": attack_type,
                "explanation_flags": explanation_flags
            }

        except Exception as e:
            print("[AI ERROR]", e)
            return self._safe_result()

    # -------------------------------------
    # SAFE RESULT
    # -------------------------------------

    def _safe_result(self):

        return {
            "predicted_class_index": 0,
            "supervised_score": 0.0,
            "anomaly_score": 0.0,
            "final_threat_score": 0.0,
            "confidence": 0.0,
            "threat_level": "NORMAL",
            "attack_type": "NORMAL",
            "explanation_flags": {}
        }