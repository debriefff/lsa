### Overview

Python based semantic full-text search engine.

Classic full-text search systems use similar algorithms for index building and search and ther have foundamental problems. They are: 

1. Synonymy - description something using different words

2. Polysemy - one word has different meanings in different contexts  

3. Ignoring semantic relations between terms in document and documents in collection  

The main project idea is to provide full-text search without described shortcoming using [LSI algorithms](https://en.wikipedia.org/wiki/Latent_semantic_indexing). The engine should be able to understand hidden (latent) semantic relations between terms in document. Desired documents shoult be in search results even they include no words from search query.

Also popular text search solution works as client-servers. This projects is pluggable module with easy to use API for any python based projects.

### Architecture

Main parts are:

1. Core represents math algorithms and has private api for search machine.

2. Search machine has public api for external modules, can ask core to do smth (build semantic space, add document to it, search, etc).

3. Database backends. Search machine doesn't depends on used database. That modeles are pluggable, their work is extracting and providing data from database to search machine and futher to core. Now project supports PostgreSQL, MySQL and SQLite.

4. Index backends. Pluggable modules to keep semantic space in search index. Now available only JSON-backedn.

### Usage

Add search engine as a git-submodule to your project. I know this is not pretty awesome, pypi-package will be added soon

    git submodule add https://github.com/Skycker/lsa


Make instance of `SearchMachine` class with exact settings and run its methods. The institutionalization process doesn't start any heavy computations. Feel free to make class instance as many times as you need. 

```
from lsa.search.machine import SearchMachine

sm = SearchMachine(latent_dimensions=150, index_backend='lsa.keeper.backends.JsonIndexBackend',
                   keep_index_info={'path_to_index_folder': 'index'},
                   db_backend='lsa.db.mysql.MySQLBackend',
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

### Methods

*Build index*. Make semantic space and save it on disk with choosen index-backend. Data will be taken from DB according to provided settings.

    sm.build_index()

*Rebuild index*. Remove previoul index and make new one.

    sm.rebuild_index()
    
*Draw semantic space*. Just for fun. Works only if latent demensions `k == 2`. Makes .png file in the script folder.
  
    sm.draw_space()

*Search*

    sm.search('natural language query', with_distances=True, limit=10)
    
If `with_distances` is True the method returns list of tuples. Each tuple is pair of document id and float number (destince from query to document. The less distance the more relevant text).

`limit` - like SQL `LIMIT`

*Remove index*. Delete all index files from disk

    sm.remove_index()
    
*Remove socument from space*

    sm.remove_document(doc_id)

*Add document to built semantic space*. Building space is not very fast process. There is apportunity to add document to search index without full rebuilding.

    sm.update_space_with_document(document, desired_id)

`document` - raw document text.

`desired_id` - id of document to return in `search` method. Value should be unique. Primary key from database table record is the most suitable value.  





