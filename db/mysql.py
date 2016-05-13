import pymysql.cursors

from lsa.db import base
from lsa.utils import exceptions


class MySQLBackend(base.DataBaseBackend):
    def __init__(self, **credentials):
        self.db_name = credentials.get('db_name', None)
        self.user = credentials.get('user', None)
        self.password = credentials.get('password', None)
        self.host = credentials.get('host', 'localhost')
        self.charset = credentials.get('charset', 'utf8')

        if self.db_name is None or self.user is None or self.password is None:
            raise exceptions.DBImproperlyConfigured

    def select(self, table_name, fields, pk_field_name, where_clause):
        connection = pymysql.connect(host=self.host, user=self.user, passwd=self.password, db=self.db_name,
                                     charset=self.charset, cursorclass=pymysql.cursors.Cursor)
        query = self.make_select_sql(table_name, fields, pk_field_name, where_clause)

        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
            return result
        finally:
            connection.close()
