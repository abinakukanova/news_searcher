import numpy as np 
import pickle
from preprocessing import (get_tokens, lemmatize, compute_cos_similarity,
            range_texts, doc_info, remove_punctuation, text_lowercase)
from gensim.models import FastText
from time import time
from collections.abc import Mapping

class FastTextSearcher():
    """
    Class for searching through a FastText index.

    Attributes:
        model: The FastText model.
        doc_info: Object containing information about the documents.
        matrix: The FastText index matrix.
    """

    def __init__(self, model_file_name="cc.ru.300.bin", fasttext_index_matrix='', doc_info=doc_info):
        """
        Initializes the FastTextSearcher object.

        Args:
            model_file_name: Path to the FastText model file.
            fasttext_index_matrix: Path to the FastText index matrix file.
            doc_info: Object containing information about the documents.
        """
        self.model = FastText.load_fasttext_format(model_file_name)
        self.doc_info = doc_info
        if fasttext_index_matrix:
            self.matrix = self.load(fasttext_index_matrix)
        else:
            self.matrix = self.index()


    def load(self, fasttext_index_matrix):
        """
        Loads the FastText index matrix from a file.

        Args:
            fasttext_index_matrix: Path to the FastText index matrix file.

        Returns:
            The loaded FastText index matrix.
        """
        try:
            with open(fasttext_index_matrix, 'rb') as f:
                matrix = pickle.load(f)
            return matrix
        except FileNotFoundError as ex:
            return self.index()

    def fasttext_transform(self, lemmas):
        """
        Transforms a list of lemmas into a FastText vector.

        Args:
            lemmas: List of lemmas.

        Returns:
            The FastText vector representing the list of lemmas.
        """
        zeros_matrix = np.zeros((len(lemmas), self.model.vector_size))
        doc_vector = np.zeros((self.model.vector_size,))
        for idx, lemma in enumerate(lemmas):
            if lemma in self.model.wv: 
                try:
                    zeros_matrix[idx] = self.model.wv[lemma]
                except AttributeError as e: 
                    print('No such word in vocabulary')
        if zeros_matrix.shape[0] != 0:  
            doc_vector = np.mean(zeros_matrix, axis=0)
            return doc_vector

    def index(self, path="fasttext_index_matrix.pickle"):
        """
        Creates and saves the FastText index matrix.

        Args:
            path: Path to the file to save the index matrix.

        Returns:
            The FastText index matrix.
        """
        fasttext_matrix = []
        for text in self.doc_info.lemmatized_texts:
            fasttext_matrix.append(self.fasttext_transform(text.split()))
        final_matrix = np.array(fasttext_matrix)
        with open(path, 'wb') as f:
            pickle.dump(final_matrix, f)
        return final_matrix

    def search(self, text, n=10):
        """
        Searches for similar documents based on the input text.

        Args:
            text: The search query.
            n: Number of results to return.

        Returns:
            List of tuples containing the cosine similarity and the text of the document.
        """
        if n >= self.doc_info.num_rows:
            n = self.doc_info.num_rows - 1

        line = lemmatize(get_tokens(remove_punctuation(text_lowercase(text))))
        vector = self.fasttext_transform(line)
        cos_sim_array = [compute_cos_similarity(vector, document) for document in self.matrix]
        return [(metric, self.doc_info.docs[index]) for index, metric in range_texts(cos_sim_array)[:n]]


def main():
    start = time()
    ft = FastTextSearcher()
    print(f"loading took {time()-start} sec")
    start = time()
    print(ft.search("украина россия"))
    print(f"searching took {time()-start} sec")

if __name__ == "__main__":
    main()