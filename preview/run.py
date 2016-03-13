import os
import sys
from flask import Flask
from flask import render_template
from flask import request
import pymysql

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from machine import SearchMachine

app = Flask(__name__)

DB_HOST = 'localhost'
DB_user = 'user'
DB_PASSWORD = 'userpassword'
DB_NAME = 'news'
CHARSET = 'utf8'


def init_search_machine():
    return SearchMachine(latent_dimensions=150, index_backend='keeper.backends.JsonIndexBackend',
                         keep_index_info={'path_to_index_folder': 'index_7500'},
                         # db_backend='db.mysql.MySQLBackend',
                         # db_credentials={'db_name': 'news', 'user': 'root', 'password': '1'},
                         # tables_info={
                         #     'news_news': {'fields': ('title', 'text'), 'pk_field_name': 'id',
                         #                   'prefix': 'where id < 75001',
                         #                   'where': ''}
                         # },
                         )


CONNECTION = pymysql.connect(host=DB_HOST, user=DB_user, passwd=DB_PASSWORD, db=DB_NAME,
                             charset=CHARSET, cursorclass=pymysql.cursors.Cursor)


def get_new_by_id(id):
    query = "SELECT title, text FROM news_news WHERE id={}".format(id)

    with CONNECTION.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchone()


@app.route("/news")
def news():
    query = request.args.get('q', '')
    results = []
    if query:
        sm = init_search_machine()
        search_results = sm.search(query, with_distances=True, limit=10)

        if search_results:
            for id, distance in search_results:
                raw_res = get_new_by_id(id)
                results.append({"id": id, "title": raw_res[0], "text": raw_res[1][:500], "distance": distance})

    return render_template('news.html', results=results, query=query)


@app.route('/news/<int:post_id>')
def new(post_id):
    return render_template('new.html', new=get_new_by_id(post_id))


if __name__ == "__main__":
    app.debug = True
    app.run()
