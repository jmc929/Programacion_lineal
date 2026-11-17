from fractions import Fraction

from .fractions import to_fraction


def identity(size):
    return [
        [Fraction(int(row == column)) for column in range(size)]
        for row in range(size)
    ]


def transpose(matrix):
    if not matrix:
        return []
    return [list(column) for column in zip(*matrix)]


def matrix_vector_product(matrix, vector):
    return [
        sum((value * vector[index] for index, value in enumerate(row)), Fraction(0))
        for row in matrix
    ]


def matrix_product(left, right):
    if not left:
        return []
    if not right or not right[0]:
        return [[] for _ in left]
    columns = transpose(right)
    return [
        [
            sum((a * b for a, b in zip(row, column)), Fraction(0))
            for column in columns
        ]
        for row in left
    ]


def inverse(matrix):
    """Return the exact inverse using Gauss-Jordan elimination."""
    size = len(matrix)
    if any(len(row) != size for row in matrix):
        raise ValueError("La matriz debe ser cuadrada para calcular su inversa.")
    if size == 0:
        return []

    identity_matrix = identity(size)
    augmented = [
        [to_fraction(value) for value in row] + identity_matrix[index]
        for index, row in enumerate(matrix)
    ]

    for column in range(size):
        pivot_row = next(
            (row for row in range(column, size) if augmented[row][column] != 0),
            None,
        )
        if pivot_row is None:
            raise ValueError("La matriz de la base es singular.")
        augmented[column], augmented[pivot_row] = (
            augmented[pivot_row],
            augmented[column],
        )
        pivot = augmented[column][column]
        augmented[column] = [value / pivot for value in augmented[column]]
        for row in range(size):
            if row == column:
                continue
            factor = augmented[row][column]
            if factor != 0:
                augmented[row] = [
                    value - factor * pivot_value
                    for value, pivot_value in zip(augmented[row], augmented[column])
                ]

    return [row[size:] for row in augmented]