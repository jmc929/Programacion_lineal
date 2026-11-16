from fractions import Fraction

from ..common.pivot import choose_leaving_row, pivot_tableau


def add_cost(left, right):
    return (left[0] + right[0], left[1] + right[1])


def subtract_cost(left, right):
    return (left[0] - right[0], left[1] - right[1])


def multiply_cost(scalar, cost):
    return (scalar * cost[0], scalar * cost[1])


def compare_cost(left, right):
    """Compare lexicographically: M dominates every finite rational."""
    return (left > right) - (left < right)


def create_tableau(standard_form):
    return [
        row[:] + [standard_form.rhs[index]]
        for index, row in enumerate(standard_form.matrix)
    ]


def calculate_reduced_costs(standard_form, basis, tableau):
    costs = [
        (Fraction(-1), Fraction(0))
        if index in standard_form.artificial_indices
        else (Fraction(0), value)
        for index, value in enumerate(standard_form.objective)
    ]
    reduced = []
    for column in range(len(costs)):
        value = costs[column]
        for row_index, basic_index in enumerate(basis):
            value = subtract_cost(
                value,
                multiply_cost(tableau[row_index][column], costs[basic_index]),
            )
        reduced.append(value)
    return reduced, costs


def select_entering_column(reduced_costs):
    return next(
        (
            index
            for index, value in enumerate(reduced_costs)
            if compare_cost(value, (Fraction(0), Fraction(0))) > 0
        ),
        None,
    )


def select_leaving_row(tableau, basis, entering_column):
    if not tableau:
        return None
    return choose_leaving_row(tableau, basis, entering_column, len(tableau[0]) - 1)


def pivot(tableau, basis, leaving_row, entering_column):
    pivot_tableau(tableau, leaving_row, entering_column)
    basis[leaving_row] = entering_column


def objective_value(costs, basis, tableau):
    value = (Fraction(0), Fraction(0))
    for row_index, basic_index in enumerate(basis):
        value = add_cost(
            value,
            multiply_cost(tableau[row_index][-1], costs[basic_index]),
        )
    return value