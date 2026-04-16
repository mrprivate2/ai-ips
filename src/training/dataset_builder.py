import csv
from pathlib import Path
from datetime import datetime
import hashlib


BASE_DIR = Path(__file__).resolve().parents[2]
DATASET_PATH = BASE_DIR / "logs" / "live_training_data.csv"

EXPECTED_FEATURES = 9   # 🔥 match your sniffer output

# cache to avoid duplicates
recent_hashes = set()


def save_sample(features, attack_type):

    try:

        DATASET_PATH.parent.mkdir(exist_ok=True)

        # =============================
        # VALIDATE FEATURE SIZE
        # =============================

        if len(features) != EXPECTED_FEATURES:
            return

        # =============================
        # DEDUPLICATION (🔥 IMPORTANT)
        # =============================

        feature_str = ",".join(map(str, features))
        feature_hash = hashlib.md5(feature_str.encode()).hexdigest()

        if feature_hash in recent_hashes:
            return

        recent_hashes.add(feature_hash)

        # limit memory
        if len(recent_hashes) > 1000:
            recent_hashes.clear()

        # =============================
        # LABELING (IMPROVED)
        # =============================

        if attack_type == "NORMAL":
            label = 0
        elif attack_type in ["PORT_SCAN", "SYN_FLOOD"]:
            label = 1
        else:
            label = 1  # anomaly

        # =============================
        # CLEAN FEATURES
        # =============================

        features = [float(x) for x in features]

        # =============================
        # ROW STRUCTURE
        # =============================

        row = [
            datetime.utcnow().isoformat(),
            attack_type,   # 🔥 store type
            *features,
            label
        ]

        file_exists = DATASET_PATH.exists()

        with open(DATASET_PATH, "a", newline="") as f:

            writer = csv.writer(f)

            # header
            if not file_exists:
                header = (
                    ["timestamp", "attack_type"] +
                    [f"f{i}" for i in range(len(features))] +
                    ["label"]
                )
                writer.writerow(header)

            writer.writerow(row)

    except Exception:
        # never break IPS
        pass