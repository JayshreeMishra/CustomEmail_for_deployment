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
        self.last_loaded_time = None  
        self.model_ttl = 300  # Keep model in memory for 5 minutes
        self.setup_nltk()  

    def load_model(self):
        """Load model only if not already loaded or expired."""
        if self.model and self.preprocessor:
            if time.time() - self.last_loaded_time < self.model_ttl:
                return  

        model_path = os.path.join("artifacts", "spelling_model.pkl")
        preprocessor_path = os.path.join("artifacts", "spelling_preprocessor.pkl")

        if not os.path.exists(model_path) or not os.path.exists(preprocessor_path):
            raise CustomException("Model files not found!", sys)

        try:
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)

            with open(preprocessor_path, 'rb') as f:
                self.preprocessor = pickle.load(f)

            self.last_loaded_time = time.time()  
            print("✅ Model loaded successfully!")

        except Exception as e:
            raise CustomException(e, sys)

    def unload_model(self):
        """Unload the model after prediction to save memory."""
        self.model = None
        self.preprocessor = None
        print("🔒 Model unloaded.")

    def setup_nltk(self):
        """Ensure necessary NLTK resources are available."""
        import nltk
        nltk_data_path = os.path.join(os.getcwd(), "ml", "data")
        nltk.data.path.append(nltk_data_path)

        for resource in ['punkt', 'stopwords']:
            try:
                nltk.data.find(f'tokenizers/{resource}') if resource == 'punkt' else nltk.data.find(f'corpora/{resource}')
            except LookupError:
                nltk.download(resource, download_dir=nltk_data_path)

    def predict(self, text):
        """Predict and return corrected text along with changed words."""
        try:
            if not text:
                raise ValueError("Input text cannot be empty.")

            self.load_model()

            preprocessed_text = self.preprocessor.transform(pd.Series([text]))[0]
            print(f"Preprocessed text: {preprocessed_text}")  # Debugging line

            if not isinstance(preprocessed_text, str):
                raise ValueError("Preprocessed text is not a string.")

            # Ensure the function call works properly
            result = self.model.correct_spelling(preprocessed_text)
            print(f"Model output: {result}")  # Debugging line

            # Handle cases where `correct_spelling` does not return the expected format
            if isinstance(result, tuple) and len(result) == 2:
                corrected_text, changed_words = result
            else:
                corrected_text = result if isinstance(result, str) else preprocessed_text
                changed_words = []  # Ensure it is always a list

            # Ensure changed_words is iterable
            if not isinstance(changed_words, list):
                changed_words = []

            self.unload_model()

            return corrected_text, changed_words

        except Exception as e:
            raise CustomException(e, sys)
