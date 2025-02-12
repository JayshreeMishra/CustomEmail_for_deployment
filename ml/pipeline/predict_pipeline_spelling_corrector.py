import sys
import os
import pickle
import pandas as pd
from config.exception import CustomException

class SpellingPredictPipeline:
    def __init__(self):
        self.model = None
        self.preprocessor = None

    def load_model(self):
        """Load the model and preprocessor only when needed, and release memory after use."""
        model_path = os.path.join("artifacts", "spelling_model.pkl")
        preprocessor_path = os.path.join("artifacts", "spelling_preprocessor.pkl")

        if not os.path.exists(model_path) or not os.path.exists(preprocessor_path):
            print("❌ Model or preprocessor file is missing!")
            raise CustomException("Model files not found!", sys)

        try:
            with open(model_path, 'rb') as f:
                model = pickle.load(f)  # Load model temporarily
            
            with open(preprocessor_path, 'rb') as f:
                preprocessor = pickle.load(f)  # Load preprocessor temporarily

            return model, preprocessor  # Return loaded objects
        except Exception as e:
            raise CustomException(e, sys)

    def predict(self, text):
        """Load model only when needed and release memory after use."""
        try:
            model, preprocessor = self.load_model()  # Load model dynamically
            preprocessed_text = preprocessor.transform(pd.Series([text]))[0]

            if not isinstance(preprocessed_text, str):
                preprocessed_text = str(preprocessed_text)

            # Correct spelling
            spelling_corrected_text, changed_words = model.correct_spelling(preprocessed_text)

            # Correct grammar (optional)
            grammar_corrected_text, _ = model.correct_grammar(spelling_corrected_text)

            del model  # Free memory
            del preprocessor  # Free memory

            return grammar_corrected_text, changed_words

        except Exception as e:
            raise CustomException(e, sys)
