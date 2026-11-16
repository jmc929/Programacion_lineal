from fractions import Fraction

from ..common.matrix_operations import matrix_vector_product, transpose
from .basis import basis_inverse


def calculate_iteration(matrix, rhs, costs, basis):
    inverse_basis = basis_inverse(matrix, basis)
    values = matrix_vector_product(inverse_basis, rhs)
    basic_costs = [costs[column] for column in basis]
    dual_values = matrix_vector_product(transpose(inverse_basis), basic_costs)
    reduced_costs = []
    for column in range(len(costs)):
        column_values = [row[column] for row in matrix]
        reduced_costs.append(
            costs[column]
            - sum(
                (dual_values[row] * column_values[row] for row in range(len(rhs))),
                Fraction(0),
            )
        )
    objective_value = sum(
        (costs[basis[row]] * values[row] for row in range(len(basis))),
        Fraction(0),
    )
    return values, reduced_costs, objective_value, inverse_basis