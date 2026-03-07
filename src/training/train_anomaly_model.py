import pandas as pd
import joblib
import os

from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest


DATASET = "logs/live_training_data.csv"

MODEL_DIR = "src/models/saved"

os.makedirs(MODEL_DIR, exist_ok=True)


print("Loading dataset...")

df = pd.read_csv(DATASET)

# remove non-feature columns
X = df[["packet_len", "dst_port"]]

print("Training scaler...")

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

print("Training anomaly model...")

model = IsolationForest(
    contamination=0.05,
    random_state=42
)

model.fit(X_scaled)

print("Saving models...")

joblib.dump(
    scaler,
    os.path.join(MODEL_DIR, "scaler.pkl")
)

joblib.dump(
    model,
    os.path.join(MODEL_DIR, "unsupervised_model.pkl")
)

print("Done.")
