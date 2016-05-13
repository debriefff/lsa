class BaseIndexBackend():
    def dump(self, obj, file_name):
        raise NotImplemented

    def load(self, file_name, return_matrix=False):
        raise NotImplemented

    def delete_index(self):
        raise NotImplemented
