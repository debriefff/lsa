import sqlite3

from lsa.db import base
from lsa.utils import exceptions


class SQLiteBackend(base.DataBaseBackend):
    def __init__(self, **credentials):
        self.db_name = credentials.get('db_file_name', None)
        if self.db_name is None:
            raise exceptions.DBImproperlyConfigured(credentials)

    def select(self, table_name, fields, pk_field_name, where_clause):
        query = self.make_select_sql(table_name, fields, pk_field_name, where_clause)
        connection = sqlite3.connect(self.db_name)
        try:
            cursor = connection.cursor()
            cursor.execute(query)
            res = cursor.fetchall()
        finally:
            connection.close()
        return res
