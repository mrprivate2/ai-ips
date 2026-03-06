import pandas as pd
import joblib
import os
from sklearn.ensemble import RandomForestClassifier

DATASET = "logs/live_training_data.csv"
MODEL_PATH = "src/models/saved/self_learning_model.pkl"


def retrain_model():

    if not os.path.exists(DATASET):
        print("[TRAINING] Dataset not found")
        return

    df = pd.read_csv(DATASET)

    if len(df) < 50:
        print("[TRAINING] Not enough samples yet")
        return

    if "label" not in df:
        print("[TRAINING] Missing labels")
        return

    X = df.drop(columns=["label"])
    y = df["label"]

    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10
    )

    model.fit(X, y)

    joblib.dump(model, MODEL_PATH)

    print(f"[AI TRAINING] Model retrained with {len(df)} samples")