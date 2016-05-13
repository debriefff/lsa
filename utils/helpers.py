import importlib

import numpy as np

from lsa.utils import exceptions


def truncate_columns(matrix, limit):
    """ Work with numpy matrices """

    if limit < 1:
        raise exceptions.TruncateMatrixError(limit)

    lst = []
    matrix = matrix.tolist()
    for row in matrix:
        lst.append(row[:limit])
    return np.matrix(lst)


def truncate_rows(matrix, limit):
    if limit < 1:
        raise exceptions.TruncateMatrixError(limit)
    return matrix[:limit]


def get_matrix_row(matrix, n):
    """ Take matrix row with number n
    Returns:
        type of return object - scalar python list
    """
    return matrix[n, :].tolist()[0]


def get_matrix_column(matrix, n):
    """ Take matrix column with number n
    Returns:
        type of return object - scalar python list
    """
    return matrix[:, n].flatten().tolist()[0]


def insert_column_to_matrix(matrix, to_insrt):
    """ Insert column into nampy matrix (to the end of matrix)

    Returns:
        type of return object - numpy.matrix
    """

    tmp = matrix.T.tolist()
    tmp.append(to_insrt)
    return np.matrix(tmp).T


def lower_document(document):
    return document.lower()


def import_from_package_and_module(path):
    """ Import via path like my_package.my_module.my_class
        It will return my_class object (class obj, not instance)
    """
    parts = path.split('.')
    cls_name, other = parts[-1], '.'.join(parts[:-1])
    mod = importlib.import_module(other)
    return getattr(mod, cls_name)
