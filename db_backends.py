import exceptions
import sqlite3
import pymysql.cursors


class DataBaseBackend(object):
    def make_select_sql(self, table_name, fields, pk_field_name):
        query_fields = [pk_field_name] + list(fields)
        return "SELECT %(fields)s FROM %(table)s;" % {'fields': ','.join(query_fields), 'table': table_name}

    def select(self, table_name, fields, pk_field_name):
        raise NotImplemented


class MySQLBackend(DataBaseBackend):
    def __init__(self, **credentials):
        self.db_name = credentials.get('db_name', None)
        self.user = credentials.get('user', None)
        self.password = credentials.get('password', None)
        self.host = credentials.get('host', 'localhost')
        self.charset = credentials.get('charset', 'utf8')

        if self.db_name is None or self.user is None or self.password is None:
            raise exceptions.DBImproperlyConfigured

    def select(self, table_name, fields, pk_field_name):
        connection = pymysql.connect(host=self.host, user=self.user, passwd=self.password, db=self.db_name,
                                     charset=self.charset, cursorclass=pymysql.cursors.Cursor)
        query = self.make_select_sql(table_name, fields, pk_field_name)

        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
            return result
        finally:
            connection.close()


class PostgreSQLBackend():
    pass


class SQLiteBackend(DataBaseBackend):
    def __init__(self, **credentials):
        self.db_name = credentials.get('db_file_name', None)
        if self.db_name is None:
            raise exceptions.DBImproperlyConfigured(credentials)

    def select(self, table_name, fields, pk_field_name):
        query = self.make_select_sql(table_name, fields, pk_field_name)
        connection = sqlite3.connect(self.db_name)
        try:
            cursor = connection.cursor()
            cursor.execute(query)
            res = cursor.fetchall()
        finally:
            connection.close()
        return res