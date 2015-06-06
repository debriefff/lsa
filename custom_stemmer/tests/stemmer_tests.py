import unittest
from custom_stemmer import porter


class TestCustomPorterStemmer(unittest.TestCase):
    """ Use trusted pairs word-stemmed_word from Martin Porter website """

    def setUp(self):
        self.stemmer = porter.Stemmer()

    def test_stem_method(self):
        with open('together.txt', 'r') as file:
            for line in file.readlines():
                word, stemmed = line.split(' ')
                custom_stemmed = self.stemmer.stem(word.strip())
                self.assertEqual(custom_stemmed, stemmed.strip())

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCustomPorterStemmer)
    unittest.TextTestRunner(verbosity=3).run(suite)