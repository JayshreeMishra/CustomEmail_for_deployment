import sys
import os
import pickle
import pandas as pd
import time
from config.exception import CustomException

class SpellingPredictPipeline:
    def __init__(self):
        self.model = None
        self.preprocessor = None
        self.last_loaded_time = None  # Track when model was loaded
        self.model_ttl = 300  # Model expires after 5 minutes

    def load_model(self):
        """Load model only if not already loaded or if expired."""
        if self.model and self.preprocessor:
            elapsed_time = time.time() - self.last_loaded_time
            if elapsed_time < self.model_ttl:
                return  # Reuse the model to avoid unnecessary reloading

        model_path = os.path.join("artifacts", "spelling_model.pkl")
        preprocessor_path = os.path.join("artifacts", "spelling_preprocessor.pkl")

        print(f"🔍 Checking model path: {model_path}, Exists? {os.path.exists(model_path)}")
        print(f"🔍 Checking preprocessor path: {preprocessor_path}, Exists? {os.path.exists(preprocessor_path)}")

        if not os.path.exists(model_path) or not os.path.exists(preprocessor_path):
            raise CustomException("Model files not found!", sys)

        try:
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)

            with open(preprocessor_path, 'rb') as f:
                self.preprocessor = pickle.load(f)

            self.last_loaded_time = time.time()  # Update load time
            print("✅ Model loaded successfully!")

        except Exception as e:
            raise CustomException(e, sys)

    def predict(self, text):
        """Load model if needed and predict."""
        try:
            self.load_model()  # Load model if expired or not loaded
            preprocessed_text = self.preprocessor.transform(pd.Series([text]))[0]

            if not isinstance(preprocessed_text, str):
                preprocessed_text = str(preprocessed_text)

            corrected_text, changed_words = self.model.correct_spelling(preprocessed_text)
           

            return corrected_text, changed_words

        except Exception as e:
            raise CustomException(e, sys)
