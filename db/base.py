class DataBaseBackend(object):
    def make_select_sql(self, table_name, fields, pk_field_name, where_clause=None):
        query_fields = [pk_field_name] + list(fields)
        where = "WHERE %s" % where_clause if where_clause else ''
        query = "SELECT %(fields)s FROM %(table)s %(where)s;" % {'fields': ','.join(query_fields), 'table': table_name,
                                                                 'where': where}
        return query

    def select(self, table_name, fields, pk_field_name, where_clause):
        raise NotImplemented
