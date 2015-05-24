# -*- coding: UTF-8 -*-
import core
import helpers
import exceptions

from decorators import with_manage_lsa_instance

# db.mysql.MySQLBackend
# db.postgres.PostgreSQLBackend
# db.sqlite.SQLiteBackend

# keeper.backends.JsonIndexBackend


class SearchMachine():
    # names to keep index
    T_INDEX_NAME = 't.json'
    S_INDEX_NAME = 's.json'
    D_INDEX_NAME = 'd.json'
    WORDS_INDEX_NAME = 'words.json'
    KEYS_INDEX_NAME = 'keys.json'

    def __init__(self, latent_dimensions, index_backend, keep_index_info, default_search_limit=100, db_backend=None,
                 db_credentials=None, tables_info=None, manage_unique=True):
        self.lsa = None
        self.default_search_limit = default_search_limit
        self.latent_dimensions = latent_dimensions
        self.manage_unique = manage_unique
        if db_backend and db_credentials and tables_info:
            self.db_backend = helpers.import_from_package_and_module(db_backend)(**db_credentials)
        self.tables_info = tables_info
        self.index_backend = helpers.import_from_package_and_module(index_backend)(**keep_index_info)

    def init_lsa(self):
        """ Create LSA instance not from dump """

        self.lsa = core.LSA(self.latent_dimensions)

    def deinit_lsa(self):
        """ Delete created LSA instance """

        self.lsa = None

    def feed_from_db(self):
        # 'credentials' : { все для соединения в БД }
        # 'tables_info': {'table_name_1': {'fields': ('fname1', 'fname2', ...), 'pk_field_name': 'pk_field_name'}, 'table_name_2':{...}}

        if not hasattr(self, 'db_backend'):
            raise exceptions.DBBackendIsNotConfigured
        # TODO: прификсы для таблиц, которые будут прибавляться к первичным ключам.
        # TODO: добавить where условие в запрос

        for table in self.tables_info:
            rows = self.db_backend.select(table, self.tables_info[table]['fields'],
                                          self.tables_info[table]['pk_field_name'])
            for row in rows:
                document = ' '.join([row[i] for i in range(1, 1 + len(self.tables_info[table]['fields']))])
                self.feed_with_document(document, row[0])

    def feed_with_document(self, raw_document, desired_id=None):
        """ Give individual document to LSA algorithm """
        return self.lsa.add_document(raw_document, desired_id)

    def build_semantic_space(self):
        self.lsa.build_semantic_space(manage_unique=self.manage_unique)

    def dump_semantic_space(self):
        self.index_backend.dump(self.lsa.T, SearchMachine.T_INDEX_NAME)
        self.index_backend.dump(self.lsa.S, SearchMachine.S_INDEX_NAME)
        self.index_backend.dump(self.lsa.D, SearchMachine.D_INDEX_NAME)
        self.index_backend.dump(self.lsa.words, SearchMachine.WORDS_INDEX_NAME)
        self.index_backend.dump(self.lsa.keys, SearchMachine.KEYS_INDEX_NAME)

    def load_space_from_dump(self):
        self.init_lsa()
        self.lsa.load_from_dump(
            t=self.index_backend.load(SearchMachine.T_INDEX_NAME, return_matrix=True),
            s=self.index_backend.load(SearchMachine.S_INDEX_NAME, return_matrix=True),
            d=self.index_backend.load(SearchMachine.D_INDEX_NAME, return_matrix=True),
            words=self.index_backend.load(SearchMachine.WORDS_INDEX_NAME),
            keys=self.index_backend.load(SearchMachine.KEYS_INDEX_NAME),
        )

    def build_index(self):
        self.init_lsa()
        self.feed_from_db()

        self.build_semantic_space()
        self.dump_semantic_space()

        self.deinit_lsa()

    def remove_index(self):
        self.deinit_lsa()
        self.index_backend.delete_index()

    def rebuild_index(self):
        self.remove_index()
        self.build_index()

    @with_manage_lsa_instance
    def search(self, query, limit=None):
        return self.lsa.search(query, limit=limit or self.default_search_limit)

    @with_manage_lsa_instance
    def update_index_with_doc(self, document, desired_id=None):
        """ Use it to add a new document to already existed semantic space """

        ney_key = self.lsa.update_space_with_document(document, desired_id)
        self.dump_semantic_space()
        return ney_key

    @with_manage_lsa_instance
    def draw_space(self, **kwargs):
        self.lsa.draw_semantic_space(self, **kwargs)