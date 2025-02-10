import sys, os
import pickle
import pandas as pd
from config.exception import CustomException

class SpellingPredictPipeline:
    def __init__(self):
        self.model = None
        self.preprocessor = None

    def load_model(self):
        """Load the model and preprocessor only when needed"""
        if self.model is None or self.preprocessor is None:
            model_path = os.path.join("artifacts", "spelling_model.pkl")
            preprocessor_path = os.path.join("artifacts", "spelling_preprocessor.pkl")

            if not os.path.exists(model_path) or not os.path.exists(preprocessor_path):
                print("❌ Model or preprocessor file is missing!")
                raise CustomException("Model files not found!", sys)

            try:
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                
                with open(preprocessor_path, 'rb') as f:
                    self.preprocessor = pickle.load(f)
            except Exception as e:
                raise CustomException(e, sys)

    def predict(self, text):
        """Load the model lazily and make predictions"""
        try:
            self.load_model()  # Load the model only when needed
            preprocessed_text = self.preprocessor.transform(pd.Series([text]))[0]

            if not isinstance(preprocessed_text, str):
                preprocessed_text = str(preprocessed_text)

            # Correct spelling and track changes
            spelling_corrected_text, changed_words = self.model.correct_spelling(preprocessed_text)

            # Correct grammar (optional, if needed)
            grammar_corrected_text, _ = self.model.correct_grammar(spelling_corrected_text)

            return grammar_corrected_text, changed_words

        except Exception as e:
            raise CustomException(e, sys)
