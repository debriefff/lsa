import psycopg2

from lsa.db import base
from lsa.utils import exceptions


class PostgreSQLBackend(base.DataBaseBackend):
    def __init__(self, **credentials):
        self.db_name = credentials.get('db_name', None)
        self.user = credentials.get('user', None)
        self.password = credentials.get('password', None)
        self.host = credentials.get('host', 'localhost')

        if self.db_name is None or self.user is None or self.password is None:
            raise exceptions.DBImproperlyConfigured

    def select(self, table_name, fields, pk_field_name, where_clause):
        connection = psycopg2.connect(
            "dbname=%s user=%s password=%s host=%s" % (self.db_name, self.user, self.password, self.host))
        query = self.make_select_sql(table_name, fields, pk_field_name, where_clause)

        try:
            cursor = connection.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            return result
        finally:
            connection.close()
