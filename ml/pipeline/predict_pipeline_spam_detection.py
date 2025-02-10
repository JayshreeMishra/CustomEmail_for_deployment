import sys
import os
import pandas as pd
from config.exception import CustomException
from ml.utils import load_object

class SpamPredictPipeline:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.preprocessor = None

    def load_models(self):
        """Lazy load models only when predict() is called."""
        if self.model is None or self.vectorizer is None or self.preprocessor is None:
            try:
                model_path = os.path.join("artifacts", "spam_model.pkl")
                vectorizer_path = os.path.join("artifacts", "tfidf_vectorizer.pkl")
                preprocessor_path = os.path.join("artifacts", "spam_text_preprocessor.pkl")

                self.model = load_object(file_path=model_path)
                self.vectorizer = load_object(file_path=vectorizer_path)
                self.preprocessor = load_object(file_path=preprocessor_path)

            except Exception as e:
                raise CustomException(e, sys)

    def predict(self, features):
        try:
            self.load_models()  # Load models only when needed

            transformed_features = self.preprocessor.transform_text(features)
            vectorized_features = self.vectorizer.transform([transformed_features])  # Input must be a list

            prediction = self.model.predict(vectorized_features)

            return prediction

        except Exception as e:
            raise CustomException(e, sys)
