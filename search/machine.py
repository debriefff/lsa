from indexer import core
from utils import helpers, exceptions
from utils.decorators import with_manage_space_instance


# db.mysql.MySQLBackend
# db.postgres.PostgreSQLBackend
# db.sqlite.SQLiteBackend

# keeper.backends.JsonIndexBackend

# Divide SearchMachine into SearchMachine and Indexer, they are logically different
class SearchMachine():
    # TODO: encapsulate names it in keeper
    T_INDEX_NAME = 't.json'
    S_INDEX_NAME = 's.json'
    D_INDEX_NAME = 'd.json'
    WORDS_INDEX_NAME = 'words.json'
    KEYS_INDEX_NAME = 'keys.json'

    def __init__(self, latent_dimensions, index_backend, keep_index_info, default_search_limit=100, db_backend=None,
                 db_credentials=None, tables_info=None, manage_unique=True, use_stemming=True, use_tf_idf=True,
                 decimals=2):
        self.space = None
        self.use_tf_idf = use_tf_idf
        self.use_stemming = use_stemming
        self.decimals = decimals
        self.default_search_limit = default_search_limit
        self.latent_dimensions = latent_dimensions
        self.manage_unique = manage_unique
        if db_backend and db_credentials and tables_info:
            self.db_backend = helpers.import_from_package_and_module(db_backend)(**db_credentials)
        self.tables_info = tables_info
        self.index_backend = helpers.import_from_package_and_module(index_backend)(**keep_index_info)

    def init_space(self):
        """ Create LSA instance not from dump """

        self.space = core.Space(self.latent_dimensions, use_stemming=self.use_stemming, use_tf_idf=self.use_tf_idf,
                                decimals=self.decimals)

    def deinit_space(self):
        """ Delete created LSA instance """

        self.space = None

    def feed_from_db(self):
        """ Manage tables_info dict adn grab data from database """

        # 'credentials' : { все для соединения в БД }
        # 'tables_info': {'table_name_1': {'fields': ('fname1', 'fname2', ...), 'pk_field_name': 'pk_field_name', 'prefix': 'd_', 'where': '...'}, 'table_name_2':{...}}

        if not hasattr(self, 'db_backend'):
            raise exceptions.DBBackendIsNotConfigured

        for table in self.tables_info:
            where_clause = self.tables_info[table].get('where', None)
            rows = self.db_backend.select(table, self.tables_info[table]['fields'],
                                          self.tables_info[table]['pk_field_name'], where_clause)
            table_prefix = self.tables_info[table].get('prefix', None)
            for row in rows:
                document = ' '.join([row[i] for i in range(1, 1 + len(self.tables_info[table]['fields']))])
                desired_id = table_prefix + str(row[0]) if table_prefix else row[0]
                self.feed_with_document(document, desired_id)

    def feed_with_document(self, raw_document, desired_id):
        """ Give individual document to LSA algorithm """
        return self.space.add_document(raw_document, desired_id)

    def build_semantic_space(self):
        self.space.build_semantic_space(manage_unique=self.manage_unique)

    def dump_semantic_space(self):
        self.index_backend.dump(self.space.T, SearchMachine.T_INDEX_NAME)
        self.index_backend.dump(self.space.S, SearchMachine.S_INDEX_NAME)
        self.index_backend.dump(self.space.D, SearchMachine.D_INDEX_NAME)
        self.index_backend.dump(self.space.words, SearchMachine.WORDS_INDEX_NAME)
        self.index_backend.dump(self.space.keys, SearchMachine.KEYS_INDEX_NAME)

    def load_space_from_dump(self):
        self.init_space()
        self.space.load_from_dump(
            t=self.index_backend.load(SearchMachine.T_INDEX_NAME, return_matrix=True),
            s=self.index_backend.load(SearchMachine.S_INDEX_NAME, return_matrix=True),
            d=self.index_backend.load(SearchMachine.D_INDEX_NAME, return_matrix=True),
            words=self.index_backend.load(SearchMachine.WORDS_INDEX_NAME),
            keys=self.index_backend.load(SearchMachine.KEYS_INDEX_NAME),
        )

    def build_index(self):
        self.init_space()
        self.feed_from_db()
        self.build_semantic_space()
        self.dump_semantic_space()

        self.deinit_space()

    def remove_index(self):
        self.deinit_space()
        self.index_backend.delete_index()

    def rebuild_index(self):
        self.remove_index()
        self.build_index()

    @with_manage_space_instance
    def search(self, query, limit=None, with_distances=False):
        return self.space.search(query, with_distances, limit=limit or self.default_search_limit)

    @with_manage_space_instance
    def update_index_with_doc(self, document, desired_id):
        """ Use it to add a new document to already existed semantic space """

        ney_key = self.space.update_space_with_document(document, desired_id)
        self.dump_semantic_space()
        return ney_key

    @with_manage_space_instance
    def draw_space(self, **kwargs):
        self.space.draw_semantic_space(**kwargs)

    @with_manage_space_instance
    def remove_document(self, doc_id):
        """ Use to remove doc from already built semantic space """
        self.space.remove_document(doc_id)
        self.dump_semantic_space()
