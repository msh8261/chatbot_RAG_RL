import os
import sys

# Get the absolute path of the current file
current_file_path = os.path.abspath(__file__)
# Get the directory path of the current file
current_dir_path = os.path.dirname(current_file_path)
# Get the parent directory path
parent_dir_path = os.path.dirname(current_dir_path)
# Add the parent directory path to the sys.path
sys.path.insert(0, parent_dir_path)

import re
import string
import spacy

# Load spaCy model for NLP processing
nlp = spacy.load("en_core_web_sm")


def preprocess_query(query: str) -> str:
    """
    Preprocess user input query by cleaning, spell-checking, and parsing.
    """
    # Convert to lowercase
    query = query.lower()

    # Remove punctuation
    query = query.translate(str.maketrans("", "", string.punctuation))

    # Remove extra spaces
    query = re.sub(r"\s+", " ", query).strip()

    # Tokenize and lemmatize using spaCy
    doc = nlp(query)
    query = " ".join([token.lemma_ for token in doc if not token.is_stop])

    return query
