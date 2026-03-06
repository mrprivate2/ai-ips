import os
import pandas as pd

DATASET = "logs/live_training_data.csv"

def load_training_data():

    if not os.path.exists(DATASET):
        return pd.DataFrame()

    try:
        df = pd.read_csv(DATASET)
        return df
    except:
        return pd.DataFrame()