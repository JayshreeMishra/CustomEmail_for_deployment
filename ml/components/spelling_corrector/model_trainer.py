import os
import sys
import re
import pickle
import pandas as pd
from dataclasses import dataclass
from symspellpy import SymSpell
#from language_tool_python import LanguageTool

from config.logging_config import logger
from config.exception import CustomException


@dataclass
class SpellingModelTrainerConfig:
    trained_model_file_path: str = os.path.join("artifacts", "spelling_model.pkl")
    combined_dictionary_file_path: str = os.path.join("artifacts", "combined_dictionary.txt")


class SpellingModel:
    def __init__(self):
        self.sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
    
    def correct_spelling(self, text):
        words = re.findall(r'\w+|\W+', text)
        corrected_words = []
        changed_words = []

        for word in words:
            if word.strip() and word.isalpha():  # Only correct alphabetic words
                suggestions = self.sym_spell.lookup_compound(word, max_edit_distance=2)
                corrected_word = suggestions[0].term if suggestions else word
                
                # Handle case preservation
                if word.istitle():
                    corrected_word = corrected_word.capitalize()
                elif word.isupper():
                    corrected_word = corrected_word.upper()
                elif word.islower():
                    corrected_word = corrected_word.lower()

                if corrected_word != word:
                    changed_words.append((word, corrected_word))
                corrected_words.append(corrected_word)
            else:
                corrected_words.append(word)  # Preserve non-alphabetic characters

        corrected_text = ''.join(corrected_words)
        return corrected_text, changed_words

class SpellingModelTrainer:
    def __init__(self):
        self.model_trainer_config = SpellingModelTrainerConfig()

    def initiate_model_trainer(self, train_data_path: str, test_data_path: str):
        try:
            logger.info("Starting model training.")

            train_data = pd.read_csv(train_data_path)
            test_data = pd.read_csv(test_data_path)

            logger.info("Preparing combined dictionary for SymSpell.")
            model = SpellingModel()

            dictionary_path = self.model_trainer_config.combined_dictionary_file_path
            combined_data = pd.concat([
                pd.read_csv(r"ml/data/en-80k.txt", sep="\t", header=None, names=["term", "count"]),
                pd.read_csv(r"ml/data/core-wordnet.txt", sep="\t", header=None, names=["term", "relation", "definition"]),
                pd.read_csv(r"ml/data/teleological-links.txt", sep="\t", header=None, names=["word1", "relation", "word2"]),
                pd.read_csv(r"ml/data/morphosemantic-links.txt", sep="\t", header=None, names=["word1", "relation", "word2", "gloss1", "gloss2"])
            ])
            combined_data[['term', 'count']].to_csv(dictionary_path, sep="\t", index=False, header=False)

            model.sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1)
            logger.info("Combined dictionary saved and loaded into SymSpell.")

            logger.info("Applying spelling and grammar correction to training and testing data.")
            
            # Correct spelling for each text in the Series
            train_data['corrected_text'] = train_data['input_text'].apply(lambda x: model.correct_spelling(x)[0])
            test_data['corrected_text'] = test_data['input_text'].apply(lambda x: model.correct_spelling(x)[0])

            corrected_train_path = train_data_path.replace(".csv", "_corrected.csv")
            corrected_test_path = test_data_path.replace(".csv", "_corrected.csv")

            train_data.to_csv(corrected_train_path, index=False)
            test_data.to_csv(corrected_test_path, index=False)

            logger.info("Saving the trained SpellingModel.")
            try:
                with open(self.model_trainer_config.trained_model_file_path, 'wb') as f:
                    pickle.dump(model, f)
                logger.info(f"Model saved at {self.model_trainer_config.trained_model_file_path}.")
            except Exception as e:
                logger.error("Failed to save the model.")
                raise CustomException(e, sys)

            logger.info("Model training completed successfully.")

        except Exception as e:
            raise CustomException(e, sys)
