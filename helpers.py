import numpy as np


def truncate_columns(matrix, limit):
    """ Work with numpy matrices """

    lst = []
    matrix = matrix.tolist()
    for row in matrix:
        lst.append(row[:limit])
    return np.matrix(lst)


def truncate_rows(matrix, limit):
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
    """ Insert column into nampy matrix

    Returns:
        type of return object - numpy.matrix
    """

    tmp = matrix.T.tolist()
    tmp.append(to_insrt)
    return np.matrix(tmp).T


def lower_document(document):
    return document.lower()