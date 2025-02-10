import os, sys
import pandas as pd
from dataclasses import dataclass
from transformers import AutoTokenizer
from ml.utils import save_obj
from config.exception import CustomException
from config.logging_config import logger


@dataclass
class SpellingDataTransformationConfig:
    transformed_train_data_path: str = os.path.join("artifacts", "spelling_transformed_train.csv")
    transformed_test_data_path: str = os.path.join("artifacts", "spelling_transformed_test.csv")
    preprocessor_obj_file_path: str = os.path.join("artifacts", "spelling_preprocessor.pkl")


class Preprocessor:
    """Encapsulates preprocessing logic for text data."""

    def __init__(self, preprocess_text_fn):
        self.preprocess_text_fn = preprocess_text_fn

    def transform(self, data):
        if not isinstance(data, pd.Series):
            raise ValueError("Input data must be a pandas Series.")
        return data.apply(self.preprocess_text_fn)


class SpellingDataTransformation:
    def __init__(self):
        self.transformation_config = SpellingDataTransformationConfig()
        self.tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased', use_fast=False)

    def preprocess_text(self, text):
        """Applies basic text preprocessing: stripping and lowercasing."""
        return text.strip().lower()

    def transform_data(self, data):
        """Applies the preprocessing logic to the 'input_text' column."""
        try:
            if 'input_text' not in data.columns:
                raise ValueError("DataFrame must contain an 'input_text' column.")
            logger.info("Starting data preprocessing transformation.")
            data['input_text'] = data['input_text'].apply(self.preprocess_text)
            logger.info("Data transformation completed successfully.")
            return data
        except Exception as e:
            raise CustomException(e, sys)

    def initiate_data_transformation(self, train_data_path, test_data_path):
        """Reads, transforms, and saves training and test datasets."""
        logger.info("Entered the data transformation component.")
        try:
            train_data = pd.read_csv(train_data_path)
            test_data = pd.read_csv(test_data_path)

            logger.info("Applying data transformation to train and test datasets.")
            transformed_train_data = self.transform_data(train_data)
            transformed_test_data = self.transform_data(test_data)

            os.makedirs(os.path.dirname(self.transformation_config.transformed_train_data_path), exist_ok=True)
            transformed_train_data.to_csv(self.transformation_config.transformed_train_data_path, index=False)
            transformed_test_data.to_csv(self.transformation_config.transformed_test_data_path, index=False)
            logger.info("Transformed data saved successfully.")

            preprocessor = Preprocessor(preprocess_text_fn=self.preprocess_text)
            save_obj(file_path=self.transformation_config.preprocessor_obj_file_path, obj=preprocessor)

            return (
                self.transformation_config.transformed_train_data_path,
                self.transformation_config.transformed_test_data_path
            )

        except Exception as e:
            raise CustomException(e, sys)
