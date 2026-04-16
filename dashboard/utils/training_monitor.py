import os
import pandas as pd

DATASET = "logs/live_training_data.csv"


def load_training_data():

    # ============================
    # FILE CHECK
    # ============================

    if not os.path.exists(DATASET):
        return pd.DataFrame()

    try:
        df = pd.read_csv(DATASET)
    except Exception as e:
        print(f"[DATA LOAD ERROR] {e}")
        return pd.DataFrame()

    if df.empty:
        return df

    # ============================
    # BASIC CLEANING
    # ============================

    # remove duplicates
    df = df.drop_duplicates()

    # drop completely empty rows
    df = df.dropna(how="all")

    # ============================
    # TIMESTAMP HANDLING
    # ============================

    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df = df.dropna(subset=["timestamp"])

    # ============================
    # LABEL NORMALIZATION
    # ============================

    if "label" in df.columns:
        df["label"] = df["label"].astype(str).str.upper()

    return df