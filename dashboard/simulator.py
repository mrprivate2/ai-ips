import requests
import numpy as np
import random
import json

API_URL = "http://127.0.0.1:8000/analyze"

# Generate realistic 41-feature vector
def generate_features(is_attack=False):

    if is_attack:
        # High anomaly attack traffic
        return np.random.uniform(0.7, 1.0, 41).tolist()
    else:
        # Normal traffic
        return np.random.uniform(0.0, 0.3, 41).tolist()


def send_traffic(is_attack=False):

    payload = {
        "features": generate_features(is_attack),
        "source_ip": f"192.168.1.{random.randint(2, 250)}",
        "destination_ip": "8.8.8.8"
    }

    try:
        response = requests.post(API_URL, json=payload)
        return response.json()
    except Exception as e:
        return {"error": str(e)}