import os
import sys
import pandas as pd
from sklearn.model_selection import train_test_split
from dataclasses import dataclass

# Adding the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from config.exception import CustomException
from config.logging_config import logger

@dataclass
class SpamDataIngestionConfig:
    train_data_path: str=os.path.join("artifacts", "spam_train.csv")
    test_data_path: str=os.path.join("artifacts", "spam_test.csv")
    raw_data_path: str=os.path.join("artifacts", "spam_raw.csv")

class SpamDataIngestion:
    def __init__(self):
        self.ingestion_config= SpamDataIngestionConfig()

    def initiate_data_ingestion(self):
        logger.info("Entered the spam data ingestion component")
        try:
            df=pd.read_csv(r"ml\data\email_spam_classification.csv")
            logger.info("Read the dataset as dataframe")

            df.drop(columns=['Unnamed: 2', 'Unnamed: 3', 'Unnamed: 4'], inplace=True)
            df.rename(columns={'v1': 'Type', 'v2': 'Mail_Text'}, inplace=True)

            if 'Type' not in df.columns or 'Mail_Text' not in df.columns:
                raise CustomException("Required columns 'Type' and 'Mail_Text' are not present after renaming.", sys)

            os.makedirs(os.path.dirname(self.ingestion_config.train_data_path), exist_ok=True)

            df.to_csv(self.ingestion_config.raw_data_path, index=False, header=True)

            logger.info("Train test split initiated")
            train_set, test_set= train_test_split(df, test_size=0.2, random_state=42)

            train_set.to_csv(self.ingestion_config.train_data_path, index=False, header= True)
            test_set.to_csv(self.ingestion_config.test_data_path, index=False, header= True)

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
    obj= SpamDataIngestion()
    obj.initiate_data_ingestion()
"""

"""
This is to test data_transformation
from ml.components.spam_detection.data_transformation import SpamDataTransformation
from ml.components.spam_detection.data_transformation import SpamDataTransformationConfig

if __name__=="__main__":
    obj= SpamDataIngestion()
    train_data, test_data= obj.initiate_data_ingestion()

    data_transformation= SpamDataTransformation()
    data_transformation.initiate_data_transformation(train_data, test_data)
"""
"""
this is to test the model trainer component
from ml.components.spam_detection.data_transformation import SpamDataTransformation
from ml.components.spam_detection.data_transformation import SpamDataTransformationConfig
from ml.components.spam_detection.model_trainer import SpamModelTrainer
from ml.components.spam_detection.model_trainer import SpamModelTrainerConfig

if __name__=="__main__":
    obj= SpamDataIngestion()
    train_data, test_data= obj.initiate_data_ingestion()

    data_transformation= SpamDataTransformation()
    train_transformed_path, test_transformed_path=data_transformation.initiate_data_transformation(train_data, test_data)

    train_data = pd.read_csv(train_transformed_path)
    test_data = pd.read_csv(test_transformed_path)

    train_texts = train_data['Transformed_Text']
    train_labels = train_data['Type']
    test_texts = test_data['Transformed_Text']
    test_labels = test_data['Type']
    
    model_trainer= SpamModelTrainer()
    model_trainer.initiate_model_trainer(train_texts, train_labels, test_texts, test_labels)
"""