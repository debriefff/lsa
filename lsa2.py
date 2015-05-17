# coding: utf-8
import collections
from stops import STOP_WORDS, EXCLUDE_CHARS
from nltk.stem import SnowballStemmer
import numpy as np
import helpers


class LSA(object):
    def __init__(self, latent_dimensions=2):
        """
        Args:
           latent_dimensions: numbers of dimensions which provide reliable indexing (but less than number of
            indexed words). For visualisation enough 2 dem.

        """

        self.latent_dimensions = latent_dimensions
        self.stop_words = STOP_WORDS
        self.chars_to_exclude = EXCLUDE_CHARS
        self.stemmer = SnowballStemmer(language="russian")
        self.docs = {}  # keeps documents and their ids
        self.words = []  # keeps indexed words
        self.keys = []  # keeps documents ids может избавиться от них?

    def exclude_trash(self, document):
        for char in self.chars_to_exclude:
            document = document.replace(char, ' ')
        return document

    def exclude_stops(self, document):
        return ' '.join([word for word in document.split(' ') if word not in self.stop_words])

    def stem_document(self, document, return_text=False):
        stemmed_words = [self.stemmer.stem(w) for w in document.split(' ')]
        if return_text:
            return ' '.join(stemmed_words)
        return stemmed_words

    def prepare_document(self, document):
        document = helpers.lower_document(document)
        document = self.exclude_trash(document)
        document = self.exclude_stops(document)
        document = self.stem_document(document)
        return document

    def check_latent_dimensions(self):
        """ Check if entered by user latent dimensions (k) less than number of indexed words and documents """
        self.latent_dimensions = min(self.latent_dimensions, len(self.words), len(self.keys))

    def manage_repeating_words(self):
        """ List with indexed words should not have repeated entries """
        self.words = list(set(self.words))

    def manage_unique_words(self):
        """
        If some word has only one entry in documents we can leave it.
        This helps to save memory

        """
        counters = [collections.Counter(self.docs[key]) for key in self.keys]
        to_remove = []
        for word in self.words:
            cnt = 0
            for counter in counters:
                cnt += counter[word]
            if cnt <= 1:
                to_remove.append(word)
        self.words = list(set(self.words) - set(to_remove))

    def add_document(self, raw_document, document_id=None):
        # here documents is a list with stemmed words
        document = self.prepare_document(raw_document)
        key = document_id or len(self.docs) + 1  # проверять уникальность ключей
        self.keys.append(key)
        self.docs[key] = document
        self.words.extend(document)
        self.manage_repeating_words()

    def build_base_matrix(self):
        """
        Terms-to-documents matrix:
            Rows - indexed words
            Columns - documents

        At the intersection - how many times the word entry in the text

        """

        lst = []
        for word in self.words:
            row = []
            for key in self.keys:
                # Можно не создавать на каждом шаге объекты-счетчики, сделать это только один раз
                counter = collections.Counter(self.docs[key])
                row.append(counter[word])
            lst.append(row)

        self.X = np.matrix(lst)

    def svd(self):
        """ Singular Value Decomposition of base matrix """

        self.T, S, self.D = np.linalg.svd(self.X, full_matrices=True)

        # numpy returns S as flat array of diagonal elements, so:
        self.S = np.diag(S)

    def truncate_matrices(self):
        """ Truncate T, S and D matrices within latent_dimensions number
            The more dimensions, the bigger influence of 'noises'
            The less dimensions, the less semantic groups model can find

        """

        self.check_latent_dimensions()

        self.T = helpers.truncate_columns(self.T, self.latent_dimensions)
        self.D = helpers.truncate_rows(self.D, self.latent_dimensions)

        self.S = helpers.truncate_rows(self.S, self.latent_dimensions)
        self.S = helpers.truncate_columns(self.S, self.latent_dimensions)

    def recalculate_base_matrix(self):
        self.X = self.T * self.S * self.D