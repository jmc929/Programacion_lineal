from dataclasses import dataclass
from fractions import Fraction

from .fractions import to_fraction


@dataclass
class StandardForm:
    objective: list
    original_objective: list
    objective_factor: Fraction
    matrix: list
    rhs: list
    basis: list
    artificial_indices: set
    variable_names: list
    decision_variable_count: int


def build_standard_form(objective, matrix, rhs, senses, direction="max"):
    """Normalize an LP and create an initial feasible basis."""
    objective = [to_fraction(value) for value in objective]
    rhs = [to_fraction(value) for value in rhs]
    if not objective:
        raise ValueError("Debe existir al menos una variable de decisión.")
    if direction not in ("max", "min"):
        raise ValueError("direction debe ser 'max' o 'min'.")
    if len(matrix) != len(rhs) or len(rhs) != len(senses):
        raise ValueError("A, b y senses deben tener el mismo número de restricciones.")
    if any(len(row) != len(objective) for row in matrix):
        raise ValueError("Cada fila de A debe tener una entrada por variable.")

    normalized_matrix = [[to_fraction(value) for value in row] for row in matrix]
    normalized_senses = list(senses)
    for row_index, value in enumerate(rhs):
        if normalized_senses[row_index] not in ("<=", ">=", "="):
            raise ValueError("Cada restricción debe usar '<=', '>=' o '='.")
        if value < 0:
            rhs[row_index] = -value
            normalized_matrix[row_index] = [
                -coefficient for coefficient in normalized_matrix[row_index]
            ]
            normalized_senses[row_index] = {
                "<=": ">=",
                ">=": "<=",
                "=": "=",
            }[normalized_senses[row_index]]

    variable_names = ["x{}".format(index + 1) for index in range(len(objective))]
    basis = [None] * len(rhs)
    artificial_indices = set()
    next_column = len(objective)

    for row_index, sense in enumerate(normalized_senses):
        if sense == "<=":
            for row in normalized_matrix:
                row.append(Fraction(0))
            normalized_matrix[row_index][next_column] = Fraction(1)
            basis[row_index] = next_column
            variable_names.append("s{}".format(row_index + 1))
            next_column += 1
        elif sense == ">=":
            for row in normalized_matrix:
                row.append(Fraction(0))
            normalized_matrix[row_index][next_column] = Fraction(-1)
            variable_names.append("s{}".format(row_index + 1))
            next_column += 1
            for row in normalized_matrix:
                row.append(Fraction(0))
            normalized_matrix[row_index][next_column] = Fraction(1)
            basis[row_index] = next_column
            artificial_indices.add(next_column)
            variable_names.append("a{}".format(row_index + 1))
            next_column += 1
        else:
            for row in normalized_matrix:
                row.append(Fraction(0))
            normalized_matrix[row_index][next_column] = Fraction(1)
            basis[row_index] = next_column
            artificial_indices.add(next_column)
            variable_names.append("a{}".format(row_index + 1))
            next_column += 1

    objective_factor = Fraction(1) if direction == "max" else Fraction(-1)
    normalized_objective = [objective_factor * value for value in objective]
    normalized_objective.extend(
        [Fraction(0)] * (next_column - len(normalized_objective))
    )
    return StandardForm(
        objective=normalized_objective,
        original_objective=objective,
        objective_factor=objective_factor,
        matrix=normalized_matrix,
        rhs=rhs,
        basis=basis,
        artificial_indices=artificial_indices,
        variable_names=variable_names,
        decision_variable_count=len(objective),
    )