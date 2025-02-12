import sys, os
import pickle
import pandas as pd
from config.exception import CustomException

class SpellingPredictPipeline:
    def __init__(self):
        self.model = None
        self.preprocessor = None
        self.load_model()  # Load the model only once during initialization

    def load_model(self):
        """Load the spelling correction model and preprocessor."""
        model_path = "artifacts/spelling_model.pkl"
        preprocessor_path = "artifacts/spelling_preprocessor.pkl"

        if os.path.exists(model_path) and os.path.exists(preprocessor_path):
            with open(model_path, "rb") as f:
                self.model = pickle.load(f)
            with open(preprocessor_path, "rb") as f:
                self.preprocessor = pickle.load(f)
        else:
            raise FileNotFoundError("Model or preprocessor not found!")

    def predict(self, text):
        """Perform spelling correction on the given text."""
        if not self.model or not self.preprocessor:
            raise ValueError("Model or preprocessor is not loaded properly.")

        processed_text = self.preprocessor.transform([text])  # Apply transformations
        corrected_text = self.model.correct(processed_text)  # Run model prediction
        
        return corrected_text  # Return corrected text