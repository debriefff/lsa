from fill import source
import psycopg2

docs, i = [], 1
for doc in source.docs:
    docs.append((i, 'title %s' % i, doc))
    i += 1


con = psycopg2.connect("dbname=docs user=test_user password=qwerty host=localhost")
cur = con.cursor()

cur.execute("DROP TABLE IF EXISTS documents")
cur.execute("CREATE TABLE documents(id INT PRIMARY KEY, title TEXT, content TEXT)")

query = "INSERT INTO documents (id, title, content) VALUES (%s, %s, %s)"
cur.executemany(query, docs)
con.commit()


cur.execute("SELECT * FROM documents")
res = cur.fetchall()
print(res)

con.close()
