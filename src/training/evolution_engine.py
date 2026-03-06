import os
import time
from src.training.auto_trainer import retrain_model

class ModelEvolutionEngine:

    def __init__(self, dataset_path):

        self.dataset_path = dataset_path
        self.last_size = 0

    def check(self):

        if not os.path.exists(self.dataset_path):
            return

        size = os.path.getsize(self.dataset_path)

        if size - self.last_size > 50000:
            print("🧠 Auto model retraining triggered")
            retrain_model()
            self.last_size = size