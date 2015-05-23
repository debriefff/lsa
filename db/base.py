class DataBaseBackend(object):
    def make_select_sql(self, table_name, fields, pk_field_name):
        query_fields = [pk_field_name] + list(fields)
        return "SELECT %(fields)s FROM %(table)s;" % {'fields': ','.join(query_fields), 'table': table_name}

    def select(self, table_name, fields, pk_field_name):
        raise NotImplemented