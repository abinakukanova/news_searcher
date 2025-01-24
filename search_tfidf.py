import pickle 
import numpy as np
from sklearn.preprocessing import normalize
from sklearn.feature_extraction.text import TfidfTransformer
from preprocessing import (get_tokens, lemmatize, compute_cos_similarity,
            range_texts, doc_info, remove_punctuation, text_lowercase)
from time import time 


class TfidfSearcher():
    """
    Class for searching through a TF-IDF index.

    Attributes:
        docs_info: Object containing information about the documents.
        tfidf_matrix: The TF-IDF matrix.
    """

    def __init__(self, matrix_file_name='', docs_info=doc_info):
        """
        Initializes the TfidfSearcher object.

        Args:
            matrix_file_name: Name of the file to load the TF-IDF matrix from.
            docs_info: Object containing information about the documents.
        """
        self.docs_info = docs_info
        if matrix_file_name:
            self.tfidf_matrix = self.load_matrix(matrix_file_name)
        else:
            self.tfidf_matrix = self.index_tfidf()

    def load_matrix(self, matrix_file_name):
        """
        Loads the TF-IDF matrix from a file.

        Args:
            matrix_file_name: Name of the file to load the matrix from.

        Returns:
            The loaded TF-IDF matrix.
        """
        try:
            with open(matrix_file_name, 'rb') as f:
                matrix = pickle.load(f)
            return matrix
        except FileNotFoundError as ex:
            return self.index()

    def index_tfidf(self, matrix_file_name='tfidf_index_matrix.pickle'):
        """
        Creates and saves the TF-IDF index.

        Args:
            matrix_file_name: Name of the file to save the index.

        Returns:
            The TF-IDF matrix.
        """
        tfidf_trans = TfidfTransformer()
        tfidf_matrix = normalize(tfidf_trans.fit_transform(self.docs_info.vectors).toarray())
        with open(matrix_file_name, 'wb') as f:
            pickle.dump(tfidf_matrix, f)
        return tfidf_matrix
    

    def search(self, text, n=10):
        """
        Searches for similar documents based on the input text.

        Args:
            text: The search query.
            n: Number of results to return.

        Returns:
            List of tuples containing the index of the document and the text of the document.
        """
        if n >= self.docs_info.num_rows:
            n = self.docs_info.num_rows - 1


        line = ' '.join(lemmatize(get_tokens(remove_punctuation(text_lowercase(text)))))
        vec = self.docs_info.vectorizer.transform([line]).toarray()
        norm_vec = normalize(vec).reshape(-1, 1)
        cos_sim_array = np.dot(self.tfidf_matrix, norm_vec)
        return  [(metric[0], self.docs_info.docs[index]) for index, metric in range_texts(cos_sim_array)[:n]]



def main():
    start = time()
    tfidf = TfidfSearcher("tfidf_index_matrix.pickle")
    print(f"loading took {time()-start} sec")
    start = time()
    print(tfidf.search("зеленский украина"))
    print(f"searching took {time()-start} sec")

if __name__ == "__main__":
    main()