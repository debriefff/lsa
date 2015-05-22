import exceptions
import sqlite3


class DataBaseBackend(object):
    def select(self, table_name, fields, pk_field_name):
        raise NotImplemented


class MySQLBackend(DataBaseBackend):
    def __init__(self, **credentials):
        pass

    def select(self, table_name, fields, pk_field_name):
        pass


class PostgreSQLBackend():
    pass


class SQLiteBackend(DataBaseBackend):
    def __init__(self, **credentials):
        self.db_name = credentials.get('db_file_name', None)
        if self.db_name is None:
            raise exceptions.DBImproperlyConfigured(credentials)

    def select(self, table_name, fields, pk_field_name):
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()
        query_fields = [pk_field_name] + list(fields)
        query = "SELECT %(fields)s FROM %(table)s;" % {'fields': ','.join(query_fields), 'table': table_name}
        cursor.execute(query)
        res = cursor.fetchall()
        connection.close()
        return res