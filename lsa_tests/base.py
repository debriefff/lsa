import core


TEST_DOCS = [
    "Британская полиция знает о местонахождении основателя WikiLeaks WikiLeaks",
    "В суде США начинается процесс против россиянина, рассылавшего спам",
    "Церемонию вручения Нобелевской премии мира бойкотируют 19 стран",
    "В Великобритании арестован основатель сайта Wikileaks Джулиан Ассандж",
    "Украина игнорирует церемонию вручения Нобелевской премии",
    "Шведский суд отказался рассматривать апелляцию основателя Wikileaks",
    "НАТО и США разработали планы обороны стран Балтии против России",
    "Полиция Великобритании нашла основателя WikiLeaks, но, не арестовала",
    "В Стокгольме и Осло сегодня состоится вручение Нобелевских премий"
]


class EmptyLsaFixtureMixin():
    """  Fixture creates LSA instance without documents """

    def setUp(self):
        self.lsa = core.LSA(latent_dimensions=3)

    def tearDown(self):
        del self.lsa


class LsaFixtureMixin(EmptyLsaFixtureMixin):
    """ Fixture creates LSA instance and fill it with docs """

    def setUp(self):
        super(LsaFixtureMixin, self).setUp()
        for i, doc in enumerate(TEST_DOCS):
            self.lsa.add_document(doc, desired_id=i)
            # self.lsa.build_semantic_space()


class HelpTestMethodsMixin():
    def run_method_without_args(self, obj, method):
        with self.assertRaises(TypeError):
            getattr(obj, method)()

    def wrong_arg(self, *args, obj, method, exception):
        with self.assertRaises(exception):
            getattr(obj, method)(*args)

    def get_result(self, *args, obj, method):
        return getattr(obj, method)(*args)

    def check_return_type_eq(self, *args, obj, method, correct_type):
        result = self.get_result(*args, obj=obj, method=method)
        self.assertEqual(type(result), correct_type)

    def check_return_eq(self, *args, obj, method, compare_with):
        result = self.get_result(*args, obj=obj, method=method)
        self.assertEqual(result, compare_with)