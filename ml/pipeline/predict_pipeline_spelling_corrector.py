import sys
import os
import pickle
import pandas as pd
from config.exception import CustomException

class SpellingPredictPipeline:
    def __init__(self):
        self.model, self.preprocessor = self.load_model()  # Load model once during initialization

    def load_model(self):
        """Load the model and preprocessor only once."""
        model_path = os.path.join("artifacts", "spelling_model.pkl")
        preprocessor_path = os.path.join("artifacts", "spelling_preprocessor.pkl")

        if not os.path.exists(model_path) or not os.path.exists(preprocessor_path):
            raise CustomException("Model files not found!", sys)

        try:
            with open(model_path, 'rb') as f:
                model = pickle.load(f)

            with open(preprocessor_path, 'rb') as f:
                preprocessor = pickle.load(f)

            return model, preprocessor

        except Exception as e:
            raise CustomException(e, sys)

    def predict(self, text):
        """Use the already loaded model for prediction."""
        try:
            preprocessed_text = self.preprocessor.transform(pd.Series([text]))[0]

            if not isinstance(preprocessed_text, str):
                preprocessed_text = str(preprocessed_text)

            # Correct spelling
            spelling_corrected_text, changed_words = self.model.correct_spelling(preprocessed_text)

            # Correct grammar (optional)
            grammar_corrected_text, _ = self.model.correct_grammar(spelling_corrected_text)

            return grammar_corrected_text, changed_words

        except Exception as e:
            raise CustomException(e, sys)