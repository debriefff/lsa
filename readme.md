```
from machine import SearchMachine

sm = SearchMachine(latent_dimensions=150, index_backend='keeper.backends.JsonIndexBackend',
                   keep_index_info={'path_to_index_folder': 'index'},
                   db_backend='db.mysql.MySQLBackend',
                   db_credentials={'db_name': 'news', 'user': 'user', 'password': 'user_big_password'},
                   tables_info={
                       'news_news': {'fields': ('title', 'text'), 'pk_field_name': 'id', 'prefix': '', 'where': 'id < 300'}
                   },
                   decimals=3,
                   use_tf_idf=False
                   )

sm.build_index()
res = sm.search('natural language query', with_distances=True, limit=10)
print(res)
```