from pymorphy3 import MorphAnalyzer
import pandas as pd
import numpy as np
import pickle
import re
import string
from pymorphy3 import MorphAnalyzer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize


morph = MorphAnalyzer()


def text_lowercase(text):
    """Converts text to lowercase.

    Args:
        text: Text to convert.

    Returns:
        Text in lowercase.
    """
    return text.lower()

def remove_punctuation(text):
    """Removes punctuation from text.

    Args:
        text: Text to remove punctuation from.

    Returns:
        Text without punctuation.
    """
    translator = str.maketrans('', '', string.punctuation)
    return text.translate(translator)

def get_tokens(text):
    """Splits text into tokens (words).

    Args:
        text: Text to tokenize.

    Returns:
        List of tokens.
    """
    return text.split()
    

def lemmatize(list_of_words):
    """Lemmatizes a list of words.

    Args:
        list_of_words: List of words to lemmatize.

    Returns:
        List of lemmatized words.
    """
    return [morph.parse(word)[0].normal_form for word in list_of_words]
    
def load_texts(path='ria-2023.csv', col_name='text'):
    """Loads texts from a CSV file.

    Args:
        path: Path to the CSV file.
        col_name: Name of the column with texts.

    Returns:
        Tuple of a list of cleaned texts and the number of rows in the file.
    """
    df = pd.read_csv(path)
    if df[col_name].isna().sum() != 0:
         df = df.dropna()
         num_rows = df.shape[0]
    else:
         df = pd.read_csv(path)
         num_rows = df.shape[0]
    docs = df[col_name].tolist()
    clean_texts = [remove_punctuation(text_lowercase(text)) for text in docs]
    return docs, clean_texts, num_rows

def create_matrix(texts):
    """Creates a matrix from texts using CountVectorizer.

    Args:
        texts: List of texts.

    Returns:
        Tuple of a matrix and a CountVectorizer object.
    """
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(texts)
    vectors = X.toarray()
    return vectors, vectorizer

def compute_cos_similarity(X, Y):
    """Computes the cosine similarity between two vectors.

    Args:
        X: First vector.
        Y: Second vector.

    Returns:
        Cosine similarity.
    """
    return np.inner(X, Y) / (np.linalg.norm(X) * np.linalg.norm(Y))

def range_texts(cos_sim_array):
    """Sorts texts by descending cosine similarity.

    Args:
        cos_sim_array: Array of cosine similarities.

    Returns:
        List of tuples (text index, cosine similarity).
    """
    return sorted(enumerate(cos_sim_array), key=lambda x: x[1], reverse=True)
     
class Docs():
    """Class for working with documents.

    Attributes:
        clean_texts: List of cleaned texts.
        num_rows: Number of rows in the CSV file.
        lemmatized_texts: List of lemmatized texts.
        vectors: Feature matrix.
        vectorizer: CountVectorizer object.
    """
    def __init__(self, file_name='lemmatized_vectorizer.pickle'):
        """Initializes a Docs object.

        Args:
            file_name: Name of the file to save vectorizer.
        """
        self.docs, self.clean_texts, self.num_rows = load_texts()
        self.lemmatized_texts = [' '.join(lemmatize(get_tokens(text))) for text in self.clean_texts]
        self.vectors, self.vectorizer = create_matrix(self.lemmatized_texts)
        with open(file_name, 'wb') as f:
            pickle.dump(self.vectorizer, f)

         
doc_info = Docs()