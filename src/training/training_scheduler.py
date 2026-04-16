import time
import os
import pandas as pd

from src.training.auto_trainer import retrain_model


# =============================
# CONFIG
# =============================

DATASET = "logs/live_training_data.csv"

MIN_NEW_SAMPLES = 200      # 🔥 retrain after +200 new samples
COOLDOWN = 300            # 🔥 5 minutes cooldown


# =============================
# GLOBAL STATE
# =============================

last_trained_samples = 0
last_train_time = 0


# =============================
# SAMPLE-BASED RETRAINING
# =============================

def check_retraining():

    global last_trained_samples
    global last_train_time

    if not os.path.exists(DATASET):
        return

    try:

        df = pd.read_csv(DATASET)
        current_samples = len(df)

        # =============================
        # MIN DATA CHECK
        # =============================

        if current_samples < 50:
            return

        # =============================
        # NEW DATA CHECK
        # =============================

        new_samples = current_samples - last_trained_samples

        if new_samples < MIN_NEW_SAMPLES:
            return

        # =============================
        # COOLDOWN CHECK
        # =============================

        now = time.time()

        if now - last_train_time < COOLDOWN:
            return

        # =============================
        # RETRAIN
        # =============================

        print(f"[AI TRAINING] +{new_samples} new samples → retraining")

        retrain_model()

        last_trained_samples = current_samples
        last_train_time = now

    except Exception as e:
        print("[TRAINING] Scheduler error:", e)


# =============================
# TIME-BASED RETRAINING
# =============================

def start_training_scheduler():

    global last_train_time

    while True:

        try:

            if not os.path.exists(DATASET):
                time.sleep(60)
                continue

            df = pd.read_csv(DATASET)
            current_samples = len(df)

            # only retrain if enough data exists
            if current_samples > 100:

                now = time.time()

                # ensure cooldown respected
                if now - last_train_time >= 3600 * 6:

                    print("[TRAINING] Scheduled retraining (6h)")

                    retrain_model()

                    last_train_time = now

        except Exception as e:
            print("[TRAINING] Error:", e)

        time.sleep(300)   # check every 5 min