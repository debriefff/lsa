import unittest
import string
import random
import exceptions
from lsa_tests.base import EmptyLsaFixtureMixin, LsaFixtureMixin, HelpTestMethodsMixin


class CoreExcludeTrashMethodTests(EmptyLsaFixtureMixin, HelpTestMethodsMixin, unittest.TestCase):
    def setUp(self):
        self.correct_test_document = 'A lot of text with ..,..*--* here'
        self.method_name = 'exclude_trash'
        self.correct_return_type = str
        super(CoreExcludeTrashMethodTests, self).setUp()

    def test_required_args(self):
        self.run_method_without_args(obj=self.lsa, method=self.method_name)

    def test_args_type(self):
        self.wrong_arg(45.5, obj=self.lsa, method=self.method_name, exception=AttributeError)
        self.wrong_arg(['string 1', 'string 2'], obj=self.lsa, method=self.method_name, exception=AttributeError)
        self.wrong_arg({'key': 'value'}, obj=self.lsa, method=self.method_name, exception=AttributeError)

        getattr(self.lsa, self.method_name)(self.correct_test_document)

    def test_return_type(self):
        self.check_return_type_eq(self.correct_test_document, obj=self.lsa, method=self.method_name,
                                  correct_type=self.correct_return_type)


class CoreExcludeStopsMethodTests(EmptyLsaFixtureMixin, HelpTestMethodsMixin, unittest.TestCase):
    def setUp(self):
        self.correct_test_document = 'Много текста со всякими и, отчасти и однако'
        self.method_name = 'exclude_stops'
        self.correct_return_type = list
        super(CoreExcludeStopsMethodTests, self).setUp()

    def test_required_args(self):
        self.run_method_without_args(obj=self.lsa, method=self.method_name)

    def test_args_type(self):
        self.wrong_arg(45.5, obj=self.lsa, method=self.method_name, exception=AttributeError)
        self.wrong_arg(['string 1', 'string 2'], obj=self.lsa, method=self.method_name, exception=AttributeError)
        self.wrong_arg({'key': 'value'}, obj=self.lsa, method=self.method_name, exception=AttributeError)

        getattr(self.lsa, self.method_name)(self.correct_test_document)

    def test_return_type(self):
        self.check_return_type_eq(self.correct_test_document, obj=self.lsa, method=self.method_name,
                                  correct_type=self.correct_return_type)


class CoreStemDocumentMethodTests(EmptyLsaFixtureMixin, HelpTestMethodsMixin, unittest.TestCase):
    def setUp(self):
        self.correct_test_document = ['много', "текста", "всякими"]
        self.method_name = 'stem_document'
        super(CoreStemDocumentMethodTests, self).setUp()

    def test_required_args(self):
        self.run_method_without_args(obj=self.lsa, method=self.method_name)

    def test_args_type(self):
        self.wrong_arg(45.5, obj=self.lsa, method=self.method_name, exception=TypeError)
        self.wrong_arg('some string', obj=self.lsa, method=self.method_name, exception=TypeError)
        self.wrong_arg({'key': 'value'}, obj=self.lsa, method=self.method_name, exception=TypeError)

        getattr(self.lsa, self.method_name)(self.correct_test_document)

    def test_return_type(self):
        self.check_return_type_eq(self.correct_test_document, obj=self.lsa, method=self.method_name, correct_type=list)
        self.check_return_type_eq(self.correct_test_document, True, obj=self.lsa, method=self.method_name,
                                  correct_type=str)


class CoreManageRepeatingWords(LsaFixtureMixin, HelpTestMethodsMixin, unittest.TestCase):
    def test_result_type(self):
        self.lsa.manage_repeating_words()
        self.assertEqual(type(self.lsa.words), list)


class CheckDocKey(EmptyLsaFixtureMixin, HelpTestMethodsMixin, unittest.TestCase):
    def setUp(self):
        self.test_key1 = random.randint(1, 100)
        self.test_key2 = ''.join([random.choice(string.ascii_letters) for x in range(5)]) + '_%d' % self.test_key1
        self.method_name = 'check_doc_key'
        super(CheckDocKey, self).setUp()

    def test_raise_exception(self):
        self.lsa.keys.append(self.test_key1)
        self.lsa.keys.append(self.test_key2)
        self.wrong_arg(self.test_key1, obj=self.lsa, method=self.method_name, exception=Exception)
        self.wrong_arg(self.test_key2, obj=self.lsa, method=self.method_name, exception=Exception)

    def test_invalid_arg_types(self):
        self.wrong_arg(35.8, obj=self.lsa, method=self.method_name, exception=exceptions.KeyTypeException)
        self.wrong_arg([34, 45], obj=self.lsa, method=self.method_name, exception=exceptions.KeyTypeException)
        self.wrong_arg({'key1': 18, 'key2': 'table_45'}, obj=self.lsa, method=self.method_name,
                       exception=exceptions.KeyTypeException)

    def test_return(self):
        self.check_return_eq(self.test_key1, obj=self.lsa, method=self.method_name, compare_with=self.test_key1)
        self.check_return_eq(self.test_key2, obj=self.lsa, method=self.method_name, compare_with=self.test_key2)


if __name__ == '__main__':
    suite = unittest.TestLoader()
    suite.loadTestsFromTestCase(CoreExcludeTrashMethodTests)
    suite.loadTestsFromTestCase(CoreExcludeStopsMethodTests)
    suite.loadTestsFromTestCase(CoreStemDocumentMethodTests)
    suite.loadTestsFromTestCase(CoreManageRepeatingWords)
    suite.loadTestsFromTestCase(CheckDocKey)
    unittest.TextTestRunner(verbosity=3).run(suite)