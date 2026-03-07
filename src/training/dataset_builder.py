import csv
from pathlib import Path
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parents[2]
DATASET_PATH = BASE_DIR / "logs" / "live_training_data.csv"


def save_sample(features, attack_type):

    try:

        DATASET_PATH.parent.mkdir(exist_ok=True)

        # convert label
        label = 1 if attack_type != "NORMAL" else 0

        # ensure numeric features
        features = [float(x) for x in features]

        row = [datetime.utcnow().isoformat()] + features + [label]

        file_exists = DATASET_PATH.exists()

        with open(DATASET_PATH, "a", newline="") as f:

            writer = csv.writer(f)

            if not file_exists:
                header = ["timestamp"] + [f"f{i}" for i in range(len(features))] + ["label"]
                writer.writerow(header)

            writer.writerow(row)

    except Exception:
        # IPS must never crash because of dataset logging
        pass