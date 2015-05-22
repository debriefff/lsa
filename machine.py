import core
import db_backends
import index_backends


class SearchMachine():
    def __init__(self, latent_dimensions, db_backend='mysq', index_backend='json', manage_unique=True):
        self.latent_dimensions = latent_dimensions
        self.manage_unique = manage_unique
        self.db_backend = None  # тут будет функция, которая вернет инстанс класса, ичходя их строкового параметра
        self.index_backend = None

    def init_lsa(self):
        """ Create LSA instance not from dump """

        self.lsa = core.LSA(self.latent_dimensions)

    def feed_from_db(self, tables_info):
        # 'credentials' : { все для соединения в БД }
        # 'tables_info': {'table_name_1': {'fields': ('fname1', 'fname2', ...), 'pk': 'pk_field_name'}, 'table_name_2':{...}}

        for table in tables_info:
            rows = self.db_backend.select(table, tables_info[table]['fields'], tables_info[table]['pk_field_name'])
            for row in rows:
                document = ' '.join([row[i] for i in range(1, len(tables_info[table]['fields']))])
                print(document)
                self.feed_with_document(document, row[0])

    def feed_with_document(self, raw_document, desired_id):
        """ Give individual document to LSA algorithm """

        return self.lsa.add_document(raw_document, desired_id)

    def build_semantic_space(self):
        self.lsa.build_semantic_space(manage_unique=self.manage_unique)

    def dump_semantic_space(self):
        pass

    def load_space_from_dump(self):
        pass

    def update_index_with_doc(self, raw_document, desired_id):
        """ Use it to add a new document to already existed semantic space """
        # Потом учесть, что инстанс класса LSA может быть не создан (поднять его из дампа прийдется)
        return self.lsa.update_space_with_document(raw_document, desired_id)

    def build_index(self):
        # Здесь создастся с нулся инстанс класса LSA, накормится документами, строится пространства, все это
        # потом дампится, инстанс удаляется
        # Это все запускает метод кормления из базы, кормит и дампит. Если кому-то захочется по-одному
        # отдавать документы поисковой машине, то он самостоятельно повторит все шаги этого метода и сколь угодно раз
        # вызовет метод feed_with_document()
        pass

    def search(self, query):
        # Здесь поднимается пространство из дампа, ищется
        pass
