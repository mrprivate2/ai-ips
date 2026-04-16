import pandas as pd
import joblib
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler


# =============================
# PROJECT ROOT
# =============================

BASE_DIR = Path(__file__).resolve().parents[2]

DATASET_PATH = BASE_DIR / "logs" / "live_training_data.csv"
MODEL_PATH = BASE_DIR / "src/models/saved/supervised_model.pkl"
SCALER_PATH = BASE_DIR / "src/models/saved/scaler.pkl"


# =============================
# RETRAIN MODEL
# =============================

def retrain_model():

    print("🧠 Retraining AI models...")

    # -----------------------------
    # LOAD DATASET
    # -----------------------------

    if not DATASET_PATH.exists():
        print("⚠ Dataset not found:", DATASET_PATH)
        return

    try:
        df = pd.read_csv(DATASET_PATH)
    except Exception as e:
        print("❌ Failed to read dataset:", e)
        return

    if df.empty:
        print("⚠ Dataset is empty.")
        return

    print(f"📊 Raw samples: {len(df)}")

    # -----------------------------
    # CLEAN DATA
    # -----------------------------

    if "timestamp" in df.columns:
        df = df.drop(columns=["timestamp"])

    if "label" not in df.columns:
        print("⚠ Missing label column")
        return

    df = df.dropna()

    X = df.drop(columns=["label"])
    y = df["label"]

    X = X.select_dtypes(include=["number"])

    print(f"🧪 Clean samples: {len(X)}")

    if len(X) < 20:
        print("⚠ Not enough data")
        return

    # -----------------------------
    # TRAIN / TEST SPLIT
    # -----------------------------

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # -----------------------------
    # SCALING
    # -----------------------------

    scaler = StandardScaler()

    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # -----------------------------
    # MODEL (BALANCED)
    # -----------------------------

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        class_weight="balanced",   # 🔥 important
        random_state=42,
        n_jobs=-1
    )

    # -----------------------------
    # TRAIN
    # -----------------------------

    print("⚙ Training model...")

    try:
        model.fit(X_train_scaled, y_train)
    except Exception as e:
        print("❌ Training failed:", e)
        return

    # -----------------------------
    # EVALUATION
    # -----------------------------

    y_pred = model.predict(X_test_scaled)
    acc = accuracy_score(y_test, y_pred)

    print(f"📈 Model Accuracy: {acc:.2f}")

    # -----------------------------
    # FEATURE IMPORTANCE (🔥 BIG)
    # -----------------------------

    try:
        importance = model.feature_importances_
        feature_names = X.columns

        top_features = sorted(
            zip(feature_names, importance),
            key=lambda x: x[1],
            reverse=True
        )[:5]

        print("🔬 Top Features:")
        for name, score in top_features:
            print(f"   {name}: {score:.3f}")

    except Exception:
        pass

    # -----------------------------
    # SAVE MODEL + SCALER
    # -----------------------------

    try:
        joblib.dump(model, MODEL_PATH)
        joblib.dump(scaler, SCALER_PATH)

        print("✅ Model saved:", MODEL_PATH)
        print("✅ Scaler saved:", SCALER_PATH)

    except Exception as e:
        print("❌ Save failed:", e)
        return

    print("🚀 Retraining complete")