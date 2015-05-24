# -*- coding: UTF-8 -*-
import collections
import operator
from random import choice
from stops import STOP_WORDS, EXCLUDE_CHARS
from nltk.stem import SnowballStemmer
from scipy.spatial import distance
import numpy as np
import helpers
import exceptions


class LSA(object):
    def __init__(self, latent_dimensions):
        """
        Args:
           latent_dimensions: numbers of dimensions which provide reliable indexing (but less than number of
            indexed words). For visualisation enough 2 dem.

        """
        # TODO: ввести параметр окрегления координат (сейчас 2 цифры после запятой)
        # TODO: ввести параметр юзать стемминг или нет
        self.latent_dimensions = latent_dimensions
        self.stop_words = STOP_WORDS
        self.chars_to_exclude = EXCLUDE_CHARS
        self.stemmer = SnowballStemmer(language="russian")
        self.docs = {}  # keeps documents and their ids
        self.words = []  # keeps indexed words
        self.keys = []  # keeps documents ids

    def exclude_trash(self, document):
        for char in self.chars_to_exclude:
            document = document.replace(char, ' ')
        return document

    def exclude_stops(self, document):
        return [word for word in document.split(' ') if word not in self.stop_words]

    def stem_document(self, document, return_text=False):
        # we need if w to avoid empty strings in results
        stemmed_words = [self.stemmer.stem(w) for w in document if w]
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
        """ If some word has only one entry in documents we can leave it.
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

    def check_doc_key(self, desired_id):
        """ Returns key that will indicate the document in space. This key will be returns by search method.
            If external document_id is given ist uniqueness will be checked, if not - returns max existed id + 1

            :param
             desired_id: int value or None! (to save memory)
        """

        # TODO: desired_id может быть строкой, это норм
        if desired_id is not None:
            if not isinstance(desired_id, int):
                raise exceptions.KeyTypeException(desired_id)
            if desired_id in self.keys:
                raise exceptions.UniqueKeyException(desired_id)
            return desired_id

        try:
            key = max(self.keys) + 1
        # if sequence is empty
        except ValueError:
            key = 0
        return key

    def add_document(self, raw_document, desired_id=None):
        """ Adds given document in semantic space

        :param
         raw_document - plain text
         desired_id - external id which programmer wants to associate this the raw document

        :return
         key - key which will be associated with document. Will be created if desired_id is None
        """

        # TODO: Добавить параметр force для замены существующего документа на новый.
        # TODO: а сохранение контента - проблема тех, кто будет юзать

        # here documents is a list with stemmed words
        document = self.prepare_document(raw_document)
        key = self.check_doc_key(desired_id)
        self.keys.append(key)
        self.docs[key] = document
        self.words.extend(document)
        self.manage_repeating_words()
        return key

    def build_base_matrix(self):
        """
        Terms-to-documents matrix:
            Rows - indexed words
            Columns - documents

        At the intersection - how many times the word entries in the text

        """

        lst = []
        for word in self.words:
            row = []
            for key in self.keys:
                # TODO: Можно не создавать на каждом шаге объекты-счетчики, сделать это только один раз
                counter = collections.Counter(self.docs[key])
                row.append(counter[word])
            lst.append(row)

        self.X = np.matrix(lst)

    def svd(self):
        """ Singular Value Decomposition of base matrix """

        T, S, D = np.linalg.svd(self.X, full_matrices=True)

        # numpy returns S as flat array of diagonal elements (+ round):
        self.T = np.matrix(T.round(decimals=2))
        self.S = np.matrix(np.diag(S).round(decimals=2))
        self.D = np.matrix(D.round(decimals=2))

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
        """ Rebuilding matrix X after truncating T, S and D """

        self.X = np.matrix((self.T * self.S * self.D).round(decimals=2))

    def build_semantic_space(self, manage_unique=True):
        if manage_unique:
            self.manage_unique_words()
        self.build_base_matrix()
        self.svd()
        self.truncate_matrices()
        self.recalculate_base_matrix()  # TODO: нужно ли, боольше она не используется

    def draw_semantic_space(self, file_name='semantic_space.png'):
        # TODO: ПОднимать исключения, если k > 2, ибо мы тогда не нарисуем
        import matplotlib.pyplot as plt
        from matplotlib import rc

        font = {'family': 'Verdana', 'weight': 'normal'}
        rc('font', **font)

        # coordinates of words
        words_coords = self.T.tolist()
        x = [x for [x, y] in words_coords]
        y = [y for [x, y] in words_coords]

        # coordinates of documents
        docs_coords = self.D.T.tolist()
        x1 = [x for [x, y] in docs_coords]
        y1 = [y for [x, y] in docs_coords]

        fig, ax = plt.subplots()
        plt.title('Семантическое пространство')
        # plt.xlabel(u'D1')
        # plt.ylabel(u'D2')
        ax.spines['bottom'].set_position('center')
        ax.spines['left'].set_position('center')
        ax.spines['top'].set_color('none')
        ax.spines['right'].set_color('none')
        plt.plot(x, y, 'ro', x1, y1, 'bs')
        for i, word in enumerate(self.words):
            ax.annotate(word, xy=(x[i], y[i]), xytext=(5, 5), textcoords='offset points', ha='left',
                        va=choice(['bottom', 'top']))
        for i, key in enumerate(self.keys):
            ax.annotate('T%s' % key, xy=(x1[i], y1[i]), xytext=(5, 5), textcoords='offset points', ha='left',
                        va=choice(['bottom', 'top']))

        fig.savefig(file_name)

    def make_semantic_space_coords_for_new_doc(self, new_document):
        """ We consider that semantic space is ready. Calculate new_document coordinates in it
            :param
                new_document:
                    cleared from trash document (optionally stemmed)

            :returns
             None if all words in the document are not in the space

             Dq: np.array (this is like column of self.D)
             Size Dq: 1 x self.latent_dimensions

        """

        doc_word_positions = []
        for word in new_document:
            try:
                word_pos = self.words.index(word)
                doc_word_positions.append(word_pos)
            except ValueError:
                continue
        if not doc_word_positions:
            return None

        # Xq is a term-vector of retrieval query q in semantic space. Its size: 1 x, t - number of terms in the space
        # If term is in the query its coordinate 1, else 0. Simple!
        Xq = [1 if x in doc_word_positions else 0 for x in range(len(self.words))]
        Dq = np.matrix(Xq) * self.T * self.S.I
        return np.array(Dq.tolist()[0]).round(decimals=2)

    def find_similar_documents(self, doc_coords, limit=100):
        """  Calculate cosine distances between docs and the given doc
        :param
            doc_coords:
                np.array with coordinates of given document
            limit:
                how many results (documents ids) to return
        :returns
            A sorted tuple with ids of relevant documents. The most relevant doc is the first
        """

        distances = [(self.keys[i], distance.cosine(helpers.get_matrix_column(self.D, i), doc_coords)) for i in
                     range(self.D.shape[1])]

        sorted_distanses = sorted(distances, key=operator.itemgetter(1))
        result = [doc_id for doc_id, dist in sorted_distanses[:limit]]
        return result

    def search(self, query, limit=100):
        """ We consider that retrieval query is like a new document.
            Calculate coordinates and compare with other docs
        """

        # TODO добавить функционал возвращения идентификаторов с диставниями
        q = self.prepare_document(query)
        pd_coords = self.make_semantic_space_coords_for_new_doc(q)
        if pd_coords is None:
            print('No one word from query is in semantic space')
            return None
        return self.find_similar_documents(pd_coords, limit)

    def update_space_with_document(self, document, desired_id=None):
        """ Folding-in a new document into semantic space
            See add_document method for params and returns info
        """

        clear_doc = self.prepare_document(document)
        doc_coords = self.make_semantic_space_coords_for_new_doc(clear_doc)
        new_key = self.check_doc_key(desired_id)
        self.keys.append(new_key)
        self.D = helpers.insert_column_to_matrix(self.D, doc_coords)

        return new_key

    def load_from_dump(self, t, s, d, words, keys):
        self.T = t
        self.S = s
        self.D = d
        self.words = words
        self.keys = keys