import pandas as pd
import joblib
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier


# =============================
# PROJECT ROOT
# =============================

BASE_DIR = Path(__file__).resolve().parents[2]

DATASET_PATH = BASE_DIR / "logs" / "live_training_data.csv"
MODEL_PATH = BASE_DIR / "src/models/saved/supervised_model.pkl"


# =============================
# RETRAIN MODEL
# =============================

def retrain_model():

    print("🧠 Retraining AI models...")

    # -----------------------------
    # CHECK DATASET EXISTS
    # -----------------------------

    if not DATASET_PATH.exists():
        print("⚠ Dataset not found:", DATASET_PATH)
        return

    # -----------------------------
    # LOAD DATASET
    # -----------------------------

    try:
        df = pd.read_csv(DATASET_PATH)
    except Exception as e:
        print("❌ Failed to read dataset:", e)
        return

    if df.empty:
        print("⚠ Dataset is empty. Skipping training.")
        return

    print(f"📊 Raw samples: {len(df)}")

    # -----------------------------
    # REMOVE TIMESTAMP COLUMN
    # -----------------------------

    if "timestamp" in df.columns:
        df = df.drop(columns=["timestamp"])

    # -----------------------------
    # REMOVE ROWS WITH MISSING LABEL
    # -----------------------------

    if "label" not in df.columns:
        print("⚠ Dataset missing 'label' column.")
        return

    df = df.dropna(subset=["label"])

    # -----------------------------
    # REMOVE OTHER NaN ROWS
    # -----------------------------

    df = df.dropna()

    # -----------------------------
    # SPLIT FEATURES / LABEL
    # -----------------------------

    X = df.drop(columns=["label"])
    y = df["label"]

    # keep numeric columns only
    X = X.select_dtypes(include=["number"])

    print(f"🧪 Clean training samples: {len(X)}")

    # -----------------------------
    # MINIMUM DATA CHECK
    # -----------------------------

    if len(X) < 10:
        print("⚠ Not enough samples to train model (need at least 10).")
        return

    # -----------------------------
    # TRAIN MODEL
    # -----------------------------

    print("⚙ Training RandomForest model...")

    model = RandomForestClassifier(
        n_estimators=150,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )

    try:
        model.fit(X, y)
    except Exception as e:
        print("❌ Training failed:", e)
        return

    # -----------------------------
    # SAVE MODEL
    # -----------------------------

    try:
        joblib.dump(model, MODEL_PATH)
        print("✅ Model saved to:", MODEL_PATH)
    except Exception as e:
        print("❌ Failed to save model:", e)
        return

    print("🚀 AI model retrained successfully.")