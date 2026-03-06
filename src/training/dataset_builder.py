import csv
import os
from datetime import datetime

DATASET_PATH = "logs/live_training_data.csv"


def save_sample(features, label):

    os.makedirs("logs", exist_ok=True)

    file_exists = os.path.exists(DATASET_PATH)

    with open(DATASET_PATH, "a", newline="") as f:

        writer = csv.writer(f)

        if not file_exists:
            writer.writerow([
                "timestamp",
                "packet_len",
                "dst_port",
                "label"
            ])

        writer.writerow([
            datetime.utcnow().isoformat(),
            features[0],
            features[1],
            label
        ])