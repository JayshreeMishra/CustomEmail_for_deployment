import os, sys
from datasets import load_dataset
from dataclasses import dataclass

from config.exception import CustomException
from config.logging_config import logger

# Adding the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

@dataclass
class SpellingDataIngestionConfig:
    train_data_path: str=os.path.join("artifacts", "spelling_train.csv")
    test_data_path: str=os.path.join("artifacts", "spelling_test.csv")
    raw_data_path: str=os.path.join("artifacts", "spelling_raw.csv")

class SpellingDataIngestion:
    def __init__(self):
        self.ingestion_config= SpellingDataIngestionConfig()

    def initiate_data_ingestion(self):
        logger.info("Entered the spelling data ingestion component")
        try:
            dataset=load_dataset("csv", data_files=r"ml\data\grammar_data.csv")
            logger.info("Read the dataset")

            os.makedirs(os.path.dirname(self.ingestion_config.train_data_path), exist_ok=True)

            # Save raw data
            os.makedirs(os.path.dirname(self.ingestion_config.train_data_path), exist_ok=True)
            raw_df = dataset['train'].to_pandas()
            raw_df.to_csv(self.ingestion_config.raw_data_path, index=False, header=True)

            # Split dataset
            logger.info("Splitting the dataset into train and test sets")
            split_dataset = dataset['train'].train_test_split(test_size=0.2, seed=42)
            train_df = split_dataset["train"].to_pandas()
            test_df = split_dataset["test"].to_pandas()

            # Save train and test datasets
            train_df.to_csv(self.ingestion_config.train_data_path, index=False, header=True)
            test_df.to_csv(self.ingestion_config.test_data_path, index=False, header=True)

            logger.info("Data ingestion completed")

            return(
                self.ingestion_config.train_data_path,
                self.ingestion_config.test_data_path
            )
        except Exception as e:
            raise CustomException(e, sys)
        

"""
this is to test the data ingestion component
if __name__=="__main__":
    obj= SpellingDataIngestion()
    obj.initiate_data_ingestion()
"""
"""
this is to test the data ingestion component
from ml.components.spelling_corrector.data_transformation import SpellingDataTransformation
from ml.components.spelling_corrector.data_transformation import SpellingDataTransformationConfig

if __name__=="__main__":
    obj= SpellingDataIngestion()
    train_data, test_data= obj.initiate_data_ingestion()

    data_transformation= SpellingDataTransformation()
    data_transformation.initiate_data_transformation(train_data, test_data)
"""
"""
this is to test the model trainer component
from ml.components.spelling_corrector.data_ingestion import SpellingDataIngestion
from ml.components.spelling_corrector.data_transformation import SpellingDataTransformation
from ml.components.spelling_corrector.model_trainer import SpellingModelTrainer
import pandas as pd

if __name__ == "__main__":
    # Data Ingestion
    data_ingestion = SpellingDataIngestion()
    train_data_path, test_data_path = data_ingestion.initiate_data_ingestion()

    # Data Transformation
    data_transformation = SpellingDataTransformation()
    transformed_train_data_path, transformed_test_data_path = data_transformation.initiate_data_transformation(
        train_data_path, test_data_path
    )

    # Load Transformed Data (optional, for logging or further inspection)
    train_data = pd.read_csv(transformed_train_data_path)
    test_data = pd.read_csv(transformed_test_data_path)

    # Model Training
    model_trainer = SpellingModelTrainer()
    corrected_data = model_trainer.initiate_model_trainer(
        transformed_train_data_path, transformed_test_data_path
    )
"""