# -*- coding: UTF-8 -*-
import core
import helpers
import index_backends


# db.mysql.MySQLBackend
# db.postgres.PostgreSQLBackend
# db.sqlite.SQLiteBackend

class SearchMachine():
    def __init__(self, latent_dimensions, search_res_limit=100, db_backend=None, db_credentials=None, tables_info=None,
                 manage_unique=True, keep_in_memory=False, index_backend='json'):
        self.lsa = None
        self.search_res_limit = search_res_limit
        self.keep_in_memory = keep_in_memory
        self.latent_dimensions = latent_dimensions
        self.manage_unique = manage_unique
        if db_backend and db_credentials and tables_info:
            self.db_backend = helpers.import_from_package_and_module(db_backend)(**db_credentials)
        self.tables_info = tables_info
        self.index_backend = None

    def init_lsa(self):
        """ Create LSA instance not from dump """

        self.lsa = core.LSA(self.latent_dimensions)

    def feed_from_db(self):
        # 'credentials' : { все для соединения в БД }
        # 'tables_info': {'table_name_1': {'fields': ('fname1', 'fname2', ...), 'pk': 'pk_field_name'}, 'table_name_2':{...}}

        for table in self.tables_info:
            rows = self.db_backend.select(table, self.tables_info[table]['fields'],
                                          self.tables_info[table]['pk_field_name'])
            for row in rows:
                document = ' '.join([row[i] for i in range(1, len(self.tables_info[table]['fields']))])
                print(document)
                self.feed_with_document(document, row[0])

    def feed_with_document(self, raw_document, desired_id=None):
        """ Give individual document to LSA algorithm """

        return self.lsa.add_document(raw_document, desired_id)

    def build_semantic_space(self):
        self.lsa.build_semantic_space(manage_unique=self.manage_unique)

    def dump_semantic_space(self):
        pass

    def load_space_from_dump(self):
        pass

    def build_index(self):
        self.lsa = self.init_lsa()
        if hasattr(self, 'db_backend'):
            self.feed_from_db()

        self.build_semantic_space()
        self.dump_semantic_space()

        if not self.keep_in_memory:
            self.lsa = None

    # TODO: некрасивые что-то следующие три метода, декоратор, имхо, нужен
    def search(self, query):
        if not self.lsa:
            self.lsa = self.load_space_from_dump()

        result = self.lsa.search(query, limit=self.search_res_limit)

        if not self.keep_in_memory:
            self.lsa = None
        return result

    def update_index_with_doc(self, document, desired_id=None):
        """ Use it to add a new document to already existed semantic space """

        if not self.lsa:
            self.lsa = self.load_space_from_dump()

        new_key = self.lsa.update_space_with_document(self, document, desired_id)

        if not self.keep_in_memory:
            self.lsa = None
        return new_key

    def draw_space(self, **kwargs):
        if not self.lsa:
            self.lsa = self.load_space_from_dump()

        self.lsa.draw_semantic_space(self, **kwargs)

        if not self.keep_in_memory:
            self.lsa = None
