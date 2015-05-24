class UniqueKeyException(Exception):
    def __init__(self, fail_id):
        self.fail_id = fail_id

    def __str__(self):
        return u'Desired id (%s) has been already used' % self.fail_id


class KeyTypeException(Exception):
    def __init__(self, fail_id):
        self.fail_id = fail_id

    def __str__(self):
        return u'Desired id (%s) has invalid type. Only integers are allowed' % self.fail_id


class DBImproperlyConfigured(Exception):
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return u'Not enough data to work with data base: %s' % self.data


class DBBackendIsNotConfigured(Exception):
    def __str__(self):
        return u'No any db settings provided'


class TooManyDimensionsToDraw(Exception):
    def __str__(self):
        return u'Method draw_semantic_space can be only used if latent_dimensions = 2'