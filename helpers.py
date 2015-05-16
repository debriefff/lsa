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


def lower_document(document):
    return document.lower()