import os
import sys
import pandas as pd
import nltk
import string
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from sklearn.preprocessing import LabelEncoder
from dataclasses import dataclass

from config.logging_config import logger
from config.exception import CustomException
from ml.utils import save_obj

@dataclass
class SpamDataTransformationConfig:
    transformed_data_path: str = os.path.join("artifacts", "spam_transformed_data.csv")
    preprocessor_obj_file_path: str = os.path.join('artifacts', 'spam_text_preprocessor.pkl')

class TextPreprocessor:
    def __init__(self, stemmer):
        self.stemmer = stemmer

    def transform_text(self, text):
        """
        Function for text preprocessing:
        - Lowercase conversion
        - Tokenization
        - Removing special characters
        - Removing stopwords and punctuation
        - Stemming
        """
        try:
            text = text.lower()
            text = nltk.word_tokenize(text)

            text = [i for i in text if i.isalnum()]

            stop_words = stopwords.words('english')
            text = [i for i in text if i not in stop_words and i not in string.punctuation]

            text = [self.stemmer.stem(i) for i in text]

            return ' '.join(text)

        except Exception as e:
            raise CustomException(f"Error in transform_text: {str(e)}", sys)

class SpamDataTransformation:
    def __init__(self):
        self.transformation_config = SpamDataTransformationConfig()
        self.ps = PorterStemmer()
        self.preprocessor = TextPreprocessor(self.ps)
        nltk.download('punkt')
        nltk.download('stopwords')

    def initiate_data_transformation(self, train_path, test_path):
        """
        Function for data transformation:
        - Label Encoding for 'Type' (0: ham, 1: spam)
        - Text transformation (text preprocessing)
        - Saving the transformed data and preprocessing object
        """
        try:
            train_df = pd.read_csv(train_path)
            test_df = pd.read_csv(test_path)
            logger.info("Loaded training and test data")

            encoder = LabelEncoder()
            train_df['Type'] = encoder.fit_transform(train_df['Type'])
            test_df['Type'] = encoder.transform(test_df['Type'])  

            train_df['Transformed_Text'] = train_df['Mail_Text'].apply(self.preprocessor.transform_text)
            test_df['Transformed_Text'] = test_df['Mail_Text'].apply(self.preprocessor.transform_text)

            train_df.dropna(subset=['Transformed_Text'], inplace=True)  
            train_df = train_df[train_df['Transformed_Text'].str.strip() != ''] 
            train_df.reset_index(drop=True, inplace=True)  

            test_df.dropna(subset=['Transformed_Text'], inplace=True)  
            test_df = test_df[test_df['Transformed_Text'].str.strip() != '']  
            test_df.reset_index(drop=True, inplace=True)  
            
            os.makedirs(os.path.dirname(self.transformation_config.transformed_data_path), exist_ok=True)
            train_transformed_path = self.transformation_config.transformed_data_path.replace(".csv", "_train.csv")
            test_transformed_path = self.transformation_config.transformed_data_path.replace(".csv", "_test.csv")

            train_df.to_csv(train_transformed_path, index=False, header=True)
            test_df.to_csv(test_transformed_path, index=False, header=True)

            logger.info("Data transformation completed")

            save_obj(self.transformation_config.preprocessor_obj_file_path, self.preprocessor)

            return train_transformed_path, test_transformed_path

        except Exception as e:
            raise CustomException(f"Error in initiate_data_transformation: {str(e)}", sys)
