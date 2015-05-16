# coding: utf-8
import collections
from stops import STOP_WORDS, EXCLUDE_CHARS
from nltk.stem import SnowballStemmer
import numpy as np


class LSA(object):
    def __init__(self):
        self.stop_words = STOP_WORDS
        self.chars_to_exclude = EXCLUDE_CHARS
        self.stemmer = SnowballStemmer(language="russian")
        self.docs = {}  # keeps documents and their ids
        self.words = []  # keeps indexed words
        self.keys = []  # keeps documents ids может избавиться от них?

    def lower_document(self, document):
        return document.lower()

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
        document = self.lower_document(document)
        document = self.exclude_trash(document)
        document = self.exclude_stops(document)
        document = self.stem_document(document)
        return document

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
        Matrix:
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

        self.base_matrix = np.array(lst)

    def svd(self):
        """ Singular Value Decomposition of base matrix """

        self.U, self.W, self.V = np.linalg.svd(self.base_matrix, full_matrices=True)


lsa = LSA()
docs = [
    "Британская полиция знает о местонахождении основателя WikiLeaks",
    "В суде США начинается процесс против россиянина, рассылавшего спам",
    "Церемонию вручения Нобелевской премии мира бойкотируют 19 стран",
    "В Великобритании арестован основатель сайта Wikileaks Джулиан Ассандж",
    "Украина игнорирует церемонию вручения Нобелевской премии",
    "Шведский суд отказался рассматривать апелляцию основателя Wikileaks",
    "НАТО и США разработали планы обороны стран Балтии против России",
    "Полиция Великобритании нашла основателя WikiLeaks, но, не арестовала",
    "В Стокгольме и Осло сегодня состоится вручение Нобелевских премий"
]

for d in docs:
    lsa.add_document(d)
print(len(lsa.words))
lsa.manage_unique_words()
print(len(lsa.words))
lsa.build_base_matrix()
lsa.svd()

print(lsa.base_matrix)
print(lsa.base_matrix.shape)
print('U:\n', lsa.U)
print('W:\n', lsa.W)
print('V:\n', lsa.V)
