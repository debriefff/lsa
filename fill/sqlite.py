from fill import source

import sqlite3 as lite

docs, i = [], 1
for doc in source.docs:
    docs.append((i, 'title %s' % i, doc))
    i += 1


con = lite.connect('little.db')

with con:
    cur = con.cursor()
    cur.execute("DROP TABLE IF EXISTS Document")
    cur.execute("CREATE TABLE Document(id INT, title TEXT, content TEXT)")
    cur.executemany("INSERT INTO Document VALUES(?, ?, ?)", tuple(docs))
print('Ready.')




