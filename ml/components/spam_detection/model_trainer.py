import os, sys
import pickle
from dataclasses import dataclass
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split

from config.exception import CustomException
from config.logging_config import logger
from ml.utils import save_obj, evaluate_model

@dataclass
class SpamModelTrainerConfig:
    trained_model_file_path = os.path.join('artifacts', 'spam_model.pkl')
    vectorizer_file_path = os.path.join('artifacts', 'tfidf_vectorizer.pkl')

class SpamModelTrainer:
    def __init__(self):
        self.model_trainer_config = SpamModelTrainerConfig()
    
    def initiate_model_trainer(self, train_texts, train_labels, test_texts, test_labels):
        try:
            logger.info("Starting model training")

            vectorizer = TfidfVectorizer(max_features=3000)
            X_train = vectorizer.fit_transform(train_texts)
            X_test = vectorizer.transform(test_texts)

            models = {
                "MultinomialNB": MultinomialNB(),
            }

            model_report = evaluate_model(X_train, train_labels, X_test, test_labels, models)

            model_name = max(model_report, key=lambda x: model_report[x]["Test Accuracy"])
            best_model = models[model_name]
            model_score = model_report[model_name]

            logger.info(f"Model: {model_name}, Test Accuracy: {model_score['Test Accuracy']:.4f}, "
                        f"Test Precision: {model_score['Test Precision']:.4f}")

            save_obj(file_path=self.model_trainer_config.trained_model_file_path, obj=best_model)
            save_obj(file_path=self.model_trainer_config.vectorizer_file_path, obj=vectorizer)

            return model_score["Test Accuracy"], model_score["Test Precision"]

        except Exception as e:
            raise CustomException(e, sys)
