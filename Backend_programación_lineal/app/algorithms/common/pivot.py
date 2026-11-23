from fractions import Fraction


def pivot_tableau(tableau, pivot_row, pivot_column):
    """Pivot a rational tableau in place and return it."""
    pivot = tableau[pivot_row][pivot_column]
    if pivot == 0:
        raise ValueError("No se puede pivotar sobre un cero.")

    tableau[pivot_row] = [value / pivot for value in tableau[pivot_row]]
    for row_index, row in enumerate(tableau):
        if row_index == pivot_row:
            continue
        factor = row[pivot_column]
        if factor != 0:
            tableau[row_index] = [
                value - factor * pivot_value
                for value, pivot_value in zip(row, tableau[pivot_row])
            ]
    return tableau


def choose_leaving_row(tableau, basis, entering_column, rhs_column):
    candidates = []
    for row_index, row in enumerate(tableau):
        coefficient = row[entering_column]
        if coefficient > 0:
            candidates.append((row[rhs_column] / coefficient, basis[row_index], row_index))
    if not candidates:
        return None
    return min(candidates)[2]


def compute_ratio_test(column_values, rhs_values, basis, variable_names, leaving_row=None):
    """Build detailed minimum-ratio test entries for step-by-step display."""
    entries = []
    for row_index, (coeff, rhs_val) in enumerate(zip(column_values, rhs_values)):
        eligible = coeff > 0
        ratio = (rhs_val / coeff) if eligible else None
        entries.append(
            {
                "row": row_index,
                "basic_variable": variable_names[basis[row_index]],
                "rhs": rhs_val,
                "pivot_column_value": coeff,
                "ratio": ratio,
                "eligible": eligible,
                "is_minimum": (leaving_row is not None and row_index == leaving_row),
            }
        )
    return entries


def choose_entering_column(reduced_costs, allowed_columns=None):
    allowed = set(range(len(reduced_costs))) if allowed_columns is None else set(allowed_columns)
    return next(
        (
            index
            for index, value in enumerate(reduced_costs)
            if index in allowed and value > 0
        ),
        None,
    )


def dot(left, right):
    return sum((a * b for a, b in zip(left, right)), Fraction(0))
