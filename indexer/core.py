import math

import collections
import numpy as np
import operator
from lsa.custom_stemmer import porter
from lsa.utils import helpers, exceptions
from lsa.utils.stops import STOP_WORDS, EXCLUDE_CHARS
from random import choice
from scipy.spatial import distance


class Space(object):
    def __init__(self, latent_dimensions, relevance_radius_threshold, use_stemming, use_tf_idf, decimals):
        """
        Args:
           latent_dimensions: numbers of dimensions which provide reliable indexing (but less than number of
            indexed words). For visualisation enough 2 dem.

        """

        self.use_tf_idf = use_tf_idf
        self.use_stemming = use_stemming
        self.decimals = decimals
        self.relevance_radius_threshold = relevance_radius_threshold
        self.latent_dimensions = latent_dimensions
        self.stop_words = STOP_WORDS
        self.chars_to_exclude = EXCLUDE_CHARS
        self.stemmer = porter.Stemmer()
        self.docs = {}  # keeps documents and their ids
        self.words = []  # keeps indexed words
        self.keys = []  # keeps documents ids

    def clear_self_docs(self):
        self.docs = {}  # mb del self.doc

    def exclude_trash(self, document):
        for char in self.chars_to_exclude:
            document = document.replace(char, ' ')
        return document

    def exclude_stops(self, document):
        return [word.strip() for word in document.split(' ') if word not in self.stop_words]

    def stem_document(self, document, return_text=False):
        if not isinstance(document, list):
            raise exceptions.StemArgException(document)

        # we need if w to avoid empty strings in results
        stemmed_words = [self.stemmer.stem(w) for w in document if w]
        if return_text:
            return ' '.join(stemmed_words)
        return stemmed_words

    def prepare_document(self, document):
        document = helpers.lower_document(document)
        document = self.exclude_trash(document)
        document = self.exclude_stops(document)
        if self.use_stemming:
            document = self.stem_document(document)
        return document

    def check_latent_dimensions(self):
        """ Check if entered by user latent dimensions (k) less than number of indexed words and documents """
        self.latent_dimensions = min(self.latent_dimensions, len(self.words), len(self.keys) - 1)

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

    # TODO: метод, который бы просто говорил, занят ли такой desired_id уже или нет. без исключений
    def check_doc_key(self, desired_id):
        """ Returns key that will indicate the document in space. This key will be returns by search method.
            If external document_id is given ist uniqueness will be checked, if not - returns max existed id + 1

            :param
             desired_id: int value or string (int with prefix for example)
        """
        if not isinstance(desired_id, (int, str)):
            raise exceptions.KeyTypeException(desired_id)

        if desired_id in self.keys:
            raise exceptions.UniqueKeyException(desired_id)
        return desired_id

    def add_document(self, raw_document, desired_id):
        """ Adds given document in semantic space

        :param
         raw_document - plain text
         desired_id - external id which programmer wants to associate this the raw document

        :return
         key - key which will be associated with document. Will be created if desired_id is None
        """

        # here documents is a list with stemmed words
        document = self.prepare_document(raw_document)
        key = self.check_doc_key(desired_id)
        self.keys.append(key)
        self.docs[key] = document
        self.words.extend(document)
        self.manage_repeating_words()
        return key

    def tf_idf_transform(self):
        """ TF-IDF transformation. Improves accuracy

            tf - term frequency. how many terms in each document (sum of columns)

            ids - inverse document frequency number. of documents which contains term
            (for each elem of each line: if elem is not zero sum one to counter)
        """

        XL = self.X.tolist()
        terms_in_doc = np.sum(XL, axis=0)

        docs_with_term = []
        for row in XL:
            cnt = 0
            for elem in row:
                if elem != 0:
                    cnt += 1
            docs_with_term.append(cnt)

        rows, cols = self.X.shape
        docs_number = cols
        for i in range(rows):
            for j in range(cols):
                tf = XL[i][j] / terms_in_doc[j]
                idf = math.log(float(docs_number) / docs_with_term[i])
                XL[i][j] = tf * idf

        self.X = np.matrix(np.array(XL).round(decimals=self.decimals))

    def build_base_matrix(self):
        """
        Terms-to-documents matrix:
            Rows - indexed words
            Columns - documents

        At the intersection - how many times the word entries in the text

        """

        counters = {}
        for key in self.keys:
            counters[key] = collections.Counter(self.docs[key])

        lst = []
        for word in self.words:
            row = []
            for key in self.keys:
                counter = counters[key]
                row.append(counter[word])
            lst.append(row)

        self.X = np.matrix(lst)

    def svd(self):
        """ Singular Value Decomposition of base matrix """

        x, y = self.X.shape
        if not x or not y:
            raise exceptions.SvdEmptyTarget

        T, S, D = np.linalg.svd(self.X, full_matrices=True)

        # numpy returns S as flat array of diagonal elements (+ round):
        self.T = np.matrix(T.round(decimals=self.decimals))
        self.S = np.matrix(np.diag(S).round(decimals=self.decimals))
        self.D = np.matrix(D.round(decimals=self.decimals))

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

    def build_semantic_space(self, manage_unique=True):
        if manage_unique:
            self.manage_unique_words()
        self.build_base_matrix()
        self.clear_self_docs()
        if self.use_tf_idf:
            self.tf_idf_transform()
        self.svd()
        self.truncate_matrices()

    def draw_semantic_space(self, file_name='semantic_space.png'):
        if self.latent_dimensions > 2:
            raise exceptions.TooManyDimensionsToDraw

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
        return np.array(Dq.tolist()[0]).round(decimals=self.decimals)

    def filter_distances(self, distances):
        """ Every document has some distance to the search query, even irrelevant
        This method takes relevant documents using calculated values of distance

        :param
            distances - array of float values of distances between documents and query
        """

        if not distances:
            return list()

        radius = max(*distances)
        threshold = radius * self.relevance_radius_threshold
        return [d for d in distances if d < threshold]

    # TODO: поиск сходных не только по координатам, но и по id
    def find_similar_documents(self, doc_coords, limit=100, with_distances=False):
        """  Calculate cosine distances between docs and the given doc
        :param
            doc_coords:
                np.array with coordinates of given document
            limit:
                how many results (documents ids) to return
        :returns
            A sorted tuple with ids of relevant documents. The most relevant doc is the first
        """

        results = []
        for i in range(self.D.shape[1]):
            d = distance.cosine(helpers.get_matrix_column(self.D, i), doc_coords)
            if not np.isnan(d) and d > 0:
                results.append((self.keys[i], d))

        relevant_distances = self.filter_distances([d[1] for d in results])
        relevant_results = [r for r in results if r[1] in relevant_distances]
        sorted_results = sorted(relevant_results, key=operator.itemgetter(1))
        if with_distances:
            return sorted_results[:limit]
        return [doc_id for doc_id, dist in sorted_results[:limit]]

    def search(self, query, with_distances=False, limit=100):
        """ We consider that retrieval query is like a new document.
            Calculate coordinates and compare with other docs
        """

        # TODO добавить возможность сортировать от меньшей релевантности к большей
        q = self.prepare_document(query)
        pd_coords = self.make_semantic_space_coords_for_new_doc(q)
        if pd_coords is None:
            print('No one word from query is in semantic space')
            return None
        return self.find_similar_documents(pd_coords, limit, with_distances)

    def update_space_with_document(self, document, desired_id=None):
        """ Folding-in a new document into semantic space
            See add_document method for params and returns info
        """

        new_key = self.check_doc_key(desired_id)
        self.keys.append(new_key)
        clear_doc = self.prepare_document(document)
        doc_coords = self.make_semantic_space_coords_for_new_doc(clear_doc)
        self.D = helpers.insert_column_to_matrix(self.D, doc_coords)

        return new_key

    def remove_document(self, doc_id):
        """ Remove document from built space.

        Raises:
            DocumentDoesNotExist exception if doc_id is not wrong
        """
        if doc_id not in self.keys:
            raise exceptions.DocumentDoesNotExist(doc_id)

        col_num = self.keys.index(doc_id)
        self.D = np.delete(self.D, col_num, 1)  # remove document from space
        self.keys.remove(doc_id)  # remove its pk

    def load_from_dump(self, t, s, d, words, keys):
        self.T = t
        self.S = s
        self.D = d
        self.words = words
        self.keys = keys
