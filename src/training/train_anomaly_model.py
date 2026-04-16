import pandas as pd
import joblib
import os

from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest


DATASET = "logs/live_training_data.csv"
MODEL_DIR = "src/models/saved"

os.makedirs(MODEL_DIR, exist_ok=True)


def train_anomaly_model():

    print("📥 Loading dataset...")

    if not os.path.exists(DATASET):
        print("❌ Dataset not found")
        return

    try:
        df = pd.read_csv(DATASET)
    except Exception as e:
        print("❌ Failed to load dataset:", e)
        return

    if df.empty:
        print("⚠ Dataset is empty")
        return

    print(f"📊 Total samples: {len(df)}")

    # =============================
    # CLEAN DATA
    # =============================

    # remove non-feature columns safely
    drop_cols = ["timestamp", "attack_type", "label"]

    X = df.drop(columns=[c for c in drop_cols if c in df.columns], errors="ignore")

    # keep only numeric
    X = X.select_dtypes(include=["number"])

    # drop NaN
    X = X.dropna()

    if len(X) < 20:
        print("⚠ Not enough clean data")
        return

    print(f"🧪 Training samples: {len(X)}")
    print(f"📦 Features used: {list(X.columns)}")

    # =============================
    # SCALE FEATURES
    # =============================

    print("⚙ Training scaler...")

    scaler = StandardScaler()

    try:
        X_scaled = scaler.fit_transform(X)
    except Exception as e:
        print("❌ Scaling failed:", e)
        return

    # =============================
    # TRAIN ISOLATION FOREST
    # =============================

    print("🌲 Training anomaly model...")

    model = IsolationForest(
        n_estimators=150,
        contamination=0.05,
        max_samples="auto",
        random_state=42,
        n_jobs=-1
    )

    try:
        model.fit(X_scaled)
    except Exception as e:
        print("❌ Model training failed:", e)
        return

    # =============================
    # SAVE MODELS
    # =============================

    try:

        joblib.dump(
            scaler,
            os.path.join(MODEL_DIR, "scaler.pkl")
        )

        joblib.dump(
            model,
            os.path.join(MODEL_DIR, "unsupervised_model.pkl")
        )

        print("✅ Models saved successfully")

    except Exception as e:
        print("❌ Failed to save model:", e)


# =============================
# RUN
# =============================

if __name__ == "__main__":
    train_anomaly_model()