import time
import os
import pandas as pd

from src.training.auto_trainer import retrain_model


# =============================
# DATASET CONFIG
# =============================

DATASET = "logs/live_training_data.csv"

RETRAIN_THRESHOLD = 500


# =============================
# SAMPLE BASED RETRAINING
# =============================

def check_retraining():

    if not os.path.exists(DATASET):
        return

    try:

        df = pd.read_csv(DATASET)

        samples = len(df)

        if samples >= RETRAIN_THRESHOLD and samples % RETRAIN_THRESHOLD == 0:

            print(f"[AI TRAINING] {samples} samples collected — retraining model")

            retrain_model()

    except Exception as e:

        print("[TRAINING] Scheduler error:", e)


# =============================
# TIME BASED RETRAINING
# =============================

def start_training_scheduler():

    while True:

        print("[TRAINING] Scheduled training check")

        try:

            retrain_model()

        except Exception as e:

            print("[TRAINING] Error:", e)

        # retrain every 6 hours
        time.sleep(3600 * 6)