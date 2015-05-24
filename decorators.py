def with_manage_lsa_instance(method):
    """ Decorator creates lsa instance from dump, let a method do its job and removes lsa instance.
        This allow you concentrate only on important logic of your method.

    """

    def wrapper(*args, **kwargs):
        self = args[0]  # instance of SearchMachine (self)

        if not getattr(self, 'lsa'):
            getattr(self, 'load_space_from_dump')()

        method_result = method(*args, **kwargs)

        getattr(self, 'deinit_lsa')()

        return method_result

    return wrapper