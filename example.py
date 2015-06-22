from machine import SearchMachine

sm = SearchMachine(latent_dimensions=2, index_backend='keeper.backends.JsonIndexBackend',
                   keep_index_info={'path_to_index_folder': 'index'},
                   db_backend='db.sqlite.SQLiteBackend',
                   db_credentials={'db_file_name': 'fill/little.db'},
                   tables_info={
                   'Document': {'fields': ('title', 'content'), 'pk_field_name': 'id', 'prefix': '', 'where': ''}},
                   decimals=3,
                   use_tf_idf=True
                   )

sm.build_index()
# sm.rebuild_index()
sm.draw_space()
res = sm.search('вручение Нобелевской премии', with_distances=True)
print(res)
# res = sm.search('вручение Нобелевской премии')
# print(res)
# sm.remove_document(doc_id=7)

from fill import source
for r in res:
    print(source.docs[r[0]-1], r[1])

