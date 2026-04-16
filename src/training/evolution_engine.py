import os
import time
import pandas as pd
from src.training.auto_trainer import retrain_model


class ModelEvolutionEngine:

    def __init__(self, dataset_path):

        self.dataset_path = dataset_path

        self.last_sample_count = 0
        self.last_train_time = 0

        self.min_new_samples = 50      # 🔥 retrain after +50 samples
        self.cooldown = 120           # 🔥 2 min cooldown

    # ----------------------------------
    # CHECK FOR RETRAINING
    # ----------------------------------
    def check(self):

        try:

            if not os.path.exists(self.dataset_path):
                return

            df = pd.read_csv(self.dataset_path)

            current_samples = len(df)

            # =============================
            # MIN DATA CHECK
            # =============================

            if current_samples < 20:
                return

            # =============================
            # NEW DATA CHECK
            # =============================

            new_samples = current_samples - self.last_sample_count

            if new_samples < self.min_new_samples:
                return

            # =============================
            # COOLDOWN CHECK
            # =============================

            now = time.time()

            if now - self.last_train_time < self.cooldown:
                return

            # =============================
            # TRIGGER RETRAINING
            # =============================

            print(f"🧠 Auto retraining triggered (+{new_samples} samples)")

            retrain_model()

            self.last_sample_count = current_samples
            self.last_train_time = now

        except Exception as e:
            print("[EVOLUTION] Error:", e)