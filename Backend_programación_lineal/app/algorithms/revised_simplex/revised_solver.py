from fractions import Fraction

from ..common.matrix_operations import matrix_vector_product
from ..common.pivot import choose_entering_column, choose_leaving_row, dot
from ..common.standard_form import build_standard_form
from .iterations import calculate_iteration


def _full_solution(variable_count, basis, basic_values):
    values = [Fraction(0)] * variable_count
    for index, value in zip(basis, basic_values):
        values[index] = value
    return values


def _record(form, basis, values, reduced_costs, phase_value, phase, iteration,
            entering=None, leaving=None):
    all_values = _full_solution(len(form.objective), basis, values)
    decisions = all_values[:form.decision_variable_count]
    return {
        "iteration": iteration,
        "phase": phase,
        "basic_variables": [form.variable_names[index] for index in basis],
        "basic_values": list(values),
        "variables": dict(zip(form.variable_names, all_values)),
        "solution": dict(zip(
            form.variable_names[:form.decision_variable_count], decisions
        )),
        "objective_value": dot(form.original_objective, decisions),
        "phase_objective_value": phase_value,
        "reduced_costs": dict(zip(form.variable_names, reduced_costs)),
        "entering_variable": (
            form.variable_names[entering] if entering is not None else None
        ),
        "leaving_variable": (
            form.variable_names[basis[leaving]] if leaving is not None else None
        ),
    }


def _run_phase(form, basis, costs, allowed_columns, phase, iterations, max_iterations):
    while True:
        values, reduced, phase_value, inverse_basis = calculate_iteration(
            form.matrix, form.rhs, costs, basis
        )
        entering = choose_entering_column(reduced, allowed_columns)
        if entering is None:
            iterations.append(
                _record(form, basis, values, reduced, phase_value, phase,
                        len(iterations))
            )
            return "optimal"

        direction = matrix_vector_product(
            inverse_basis,
            [row[entering] for row in form.matrix],
        )
        leaving = choose_leaving_row(
            [[value, direction[index]] for index, value in enumerate(values)],
            basis,
            1,
            0,
        )
        if leaving is None:
            iterations.append(
                _record(form, basis, values, reduced, phase_value, phase,
                        len(iterations), entering)
            )
            return "unbounded"
        if len(iterations) >= max_iterations:
            return "iteration_limit"

        iterations.append(
            _record(form, basis, values, reduced, phase_value, phase,
                    len(iterations), entering, leaving)
        )
        basis[leaving] = entering


def _remove_artificial_basics(form, basis):
    row_index = 0
    while row_index < len(basis):
        if basis[row_index] not in form.artificial_indices:
            row_index += 1
            continue

        inverse_basis = calculate_iteration(
            form.matrix, form.rhs, [Fraction(0)] * len(form.objective), basis
        )[3]
        basic_set = set(basis)
        replacement = None
        for column in range(len(form.objective)):
            if column in form.artificial_indices or column in basic_set:
                continue
            transformed_coefficient = sum(
                (
                    inverse_basis[row_index][source_row]
                    * form.matrix[source_row][column]
                    for source_row in range(len(form.rhs))
                ),
                Fraction(0),
            )
            if transformed_coefficient != 0:
                replacement = column
                break

        if replacement is not None:
            basis[row_index] = replacement
            row_index += 1
        else:
            del form.matrix[row_index]
            del form.rhs[row_index]
            del basis[row_index]


def solve_revised_simplex(
    objective,
    matrix,
    rhs,
    senses,
    direction="max",
    max_iterations=1000,
):
    """Solve an LP with the two-phase revised simplex method and exact fractions."""
    if not isinstance(max_iterations, int) or max_iterations < 1:
        raise ValueError("max_iterations debe ser un entero positivo.")
    form = build_standard_form(objective, matrix, rhs, senses, direction)
    basis = form.basis[:]
    iterations = []
    phase_one_costs = [
        Fraction(-1) if column in form.artificial_indices else Fraction(0)
        for column in range(len(form.objective))
    ]
    phase_one_status = _run_phase(
        form,
        basis,
        phase_one_costs,
        range(len(form.objective)),
        "I",
        iterations,
        max_iterations,
    )

    if phase_one_status == "iteration_limit":
        return {
            "status": phase_one_status,
            "objective_value": None,
            "solution": None,
            "iterations": iterations,
        }
    if phase_one_status == "unbounded":
        raise ArithmeticError("La fase I no puede ser no acotada.")

    values = calculate_iteration(
        form.matrix, form.rhs, phase_one_costs, basis
    )[0]
    if sum(
        (values[row] for row, column in enumerate(basis)
         if column in form.artificial_indices),
        Fraction(0),
    ) > 0:
        return {
            "status": "infeasible",
            "objective_value": None,
            "solution": None,
            "iterations": iterations,
        }

    _remove_artificial_basics(form, basis)
    allowed = [
        column
        for column in range(len(form.objective))
        if column not in form.artificial_indices
    ]
    phase_two_status = _run_phase(
        form,
        basis,
        form.objective,
        allowed,
        "II",
        iterations,
        max_iterations,
    )
    if phase_two_status == "iteration_limit":
        return {
            "status": phase_two_status,
            "objective_value": None,
            "solution": None,
            "iterations": iterations,
        }
    if phase_two_status == "unbounded":
        return {
            "status": phase_two_status,
            "objective_value": None,
            "solution": None,
            "iterations": iterations,
        }

    values = calculate_iteration(
        form.matrix, form.rhs, form.objective, basis
    )[0]
    all_values = _full_solution(len(form.objective), basis, values)
    decisions = all_values[:form.decision_variable_count]
    return {
        "status": "optimal",
        "objective_value": dot(form.original_objective, decisions),
        "solution": dict(zip(
            form.variable_names[:form.decision_variable_count], decisions
        )),
        "iterations": iterations,
    }