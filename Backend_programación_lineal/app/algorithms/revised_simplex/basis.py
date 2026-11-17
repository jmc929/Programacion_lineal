from fractions import Fraction

from ..common.matrix_operations import inverse, matrix_vector_product


def basis_matrix(matrix, basis):
    return [[row[column] for column in basis] for row in matrix]


def basis_inverse(matrix, basis):
    return inverse(basis_matrix(matrix, basis))


def basic_values(matrix, rhs, basis):
    return matrix_vector_product(basis_inverse(matrix, basis), rhs)