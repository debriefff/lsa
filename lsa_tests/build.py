import string
import unittest
import random
import exceptions
from lsa_tests.base import LsaFixtureMixin
import numpy as np
import helpers


class CoreManageUniqueWordsMethodTests(LsaFixtureMixin, unittest.TestCase):
    def make_unique_words(self):
        self.unique_words = {}
        for key in self.lsa.docs.keys():
            while True:
                tmp = ''.join([random.choice(string.ascii_letters) for x in range(30)])
                if tmp not in self.lsa.docs[key] and tmp not in self.unique_words:
                    self.unique_words[key] = tmp
                    break

    def test_unique(self):
        """ Test does it really delete all repetitions """

        self.make_unique_words()

        # input unique word in every document
        for key in self.lsa.docs.keys():
            self.lsa.docs[key].append(self.unique_words[key])
        # an put them into term storage
        self.lsa.words.extend(self.unique_words.values())

        self.lsa.manage_unique_words()
        for w in self.unique_words.values():
            self.assertNotIn(w, self.lsa.words)

    def test_result_type(self):
        self.lsa.manage_unique_words()
        self.assertEqual(type(self.lsa.words), list)


class CoreBuildBaseMatrixMethodTest(LsaFixtureMixin, unittest.TestCase):
    def setUp(self):
        self.true_matrix = np.matrix([[0, 1, 0, 0, 0, 0, 1, 0, 0],
                                      [1, 0, 0, 1, 0, 1, 0, 1, 0],
                                      [0, 0, 1, 0, 1, 0, 0, 0, 1],
                                      [0, 1, 0, 0, 0, 1, 0, 0, 0],
                                      [0, 0, 1, 0, 0, 0, 1, 0, 0],
                                      [2, 0, 0, 1, 0, 1, 0, 1, 0],
                                      [0, 0, 1, 0, 1, 0, 0, 0, 1],
                                      [0, 0, 1, 0, 1, 0, 0, 0, 1],
                                      [0, 0, 1, 0, 1, 0, 0, 0, 0],
                                      [0, 0, 0, 1, 0, 0, 0, 1, 0],
                                      [1, 0, 0, 0, 0, 0, 0, 1, 0],
                                      [0, 0, 0, 1, 0, 0, 0, 1, 0],
                                      [0, 1, 0, 0, 0, 0, 1, 0, 0]])
        self.true_matrix_empty = np.matrix([[]])
        super(CoreBuildBaseMatrixMethodTest, self).setUp()

    def test_result_type(self):
        pass

    def test_matrix(self):
        self.lsa.words = ['прот', 'основател', 'прем', 'суд', 'стран', 'wikileaks', 'нобелевск', 'вручен', 'церемон',
                          'арестова', 'полиц', 'великобритан', 'сша']
        self.lsa.build_base_matrix()
        self.assertEqual(self.lsa.X.tolist(), self.true_matrix.tolist())

    def test_with_empty_data(self):
        self.lsa.docs = {}
        self.lsa.words = []
        self.lsa.keys = []

        self.lsa.build_base_matrix()
        # assertEqual fail trying to compare numpy.matrices
        self.assertEqual(self.lsa.X.tolist(), self.true_matrix_empty.tolist())


class CoreSvdMethodTests(LsaFixtureMixin, unittest.TestCase):
    @unittest.skip
    def test_work(self):
        self.lsa.X = np.matrix([[0, 1, 0, 0, 0, 0, 1, 0, 0],
                                [1, 0, 0, 1, 0, 1, 0, 1, 0],
                                [0, 0, 1, 0, 1, 0, 0, 0, 1],
                                [0, 1, 0, 0, 0, 1, 0, 0, 0],
                                [0, 0, 1, 0, 0, 0, 1, 0, 0],
                                [2, 0, 0, 1, 0, 1, 0, 1, 0],
                                [0, 0, 1, 0, 1, 0, 0, 0, 1],
                                [0, 0, 1, 0, 1, 0, 0, 0, 1],
                                [0, 0, 1, 0, 1, 0, 0, 0, 0],
                                [0, 0, 0, 1, 0, 0, 0, 1, 0],
                                [1, 0, 0, 0, 0, 0, 0, 1, 0],
                                [0, 0, 0, 1, 0, 0, 0, 1, 0],
                                [0, 1, 0, 0, 0, 0, 1, 0, 0]])

        self.lsa.svd()
        print(self.lsa.T)
        print(self.lsa.S)
        print(self.lsa.D)

    def test_work_with_empty_data(self):
        self.lsa.X = np.matrix([[]])
        with self.assertRaises(exceptions.SvdEmptyTarget):
            self.lsa.svd()


class MatrixFixtures():
    def setUp(self):
        self.matrix = np.matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        self.normal_limit = 2
        self.bigget_limit = 7
        self.wrong_limit = -2
        self.zero_limit = 0
        self.empty_matrix = np.matrix([[]])

    def tearDown(self):
        del self.matrix
        del self.empty_matrix


class TruncateCommon(MatrixFixtures):
    def test_bigger(self):
        res = self.truncate(self.bigget_limit)
        self.assertEqual(res.shape, self.matrix.shape)

    def test_wrong(self):
        with self.assertRaises(exceptions.TruncateMatrixError):
            self.truncate(self.wrong_limit)

    def test_zero(self):
        with self.assertRaises(exceptions.TruncateMatrixError):
            self.truncate(self.zero_limit)

    def test_return_type(self):
        res = self.truncate(self.normal_limit)
        self.assertEqual(type(res), type(self.matrix))

    def test_empty(self):
        res = self.truncate(self.normal_limit, empty=True)
        self.assertEqual(res.shape, self.empty_matrix.shape)


class TruncateColumnsTests(TruncateCommon, unittest.TestCase):
    def truncate(self, limit, empty=False):
        if empty:
            return helpers.truncate_columns(self.empty_matrix, limit)
        return helpers.truncate_columns(self.matrix, limit)

    def test_normal(self):
        res = self.truncate(self.normal_limit)
        true_shape = (self.matrix.shape[0], self.normal_limit)
        self.assertEqual(res.shape, true_shape)


class TruncateRowsTests(TruncateCommon, unittest.TestCase):
    def truncate(self, limit, empty=False):
        if empty:
            return helpers.truncate_rows(self.empty_matrix, limit)
        return helpers.truncate_rows(self.matrix, limit)

    def test_normal(self):
        res = self.truncate(self.normal_limit)
        true_shape = (self.normal_limit, self.matrix.shape[1])
        self.assertEqual(res.shape, true_shape)


if __name__ == '__main__':
    suite = unittest.TestLoader()
    suite.loadTestsFromTestCase(CoreManageUniqueWordsMethodTests)
    suite.loadTestsFromTestCase(CoreBuildBaseMatrixMethodTest)
    suite.loadTestsFromTestCase(CoreSvdMethodTests)
    suite.loadTestsFromTestCase(TruncateColumnsTests)
    suite.loadTestsFromTestCase(TruncateRowsTests)
    unittest.TextTestRunner(verbosity=3).run(suite)