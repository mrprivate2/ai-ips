# =========================================
# AI-IPS Models Package
# =========================================

"""
Central access point for all AI models

This module helps:
- Organize model imports
- Keep code clean across project
- Provide reusable loaders
"""

from pathlib import Path
import joblib

# =============================
# DEFAULT MODEL PATHS
# =============================

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_DIR = BASE_DIR / "src" / "models" / "saved"

SUPERVISED_MODEL = MODEL_DIR / "supervised_model.pkl"
UNSUPERVISED_MODEL = MODEL_DIR / "unsupervised_model.pkl"
SCALER_MODEL = MODEL_DIR / "scaler.pkl"


# =============================
# LOADERS
# =============================

def load_supervised():
    try:
        return joblib.load(SUPERVISED_MODEL)
    except Exception:
        return None


def load_unsupervised():
    try:
        return joblib.load(UNSUPERVISED_MODEL)
    except Exception:
        return None


def load_scaler():
    try:
        return joblib.load(SCALER_MODEL)
    except Exception:
        return None