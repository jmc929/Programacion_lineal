from fractions import Fraction

from ..common.pivot import dot
from ..common.standard_form import build_standard_form
from .tableau import (
    calculate_reduced_costs,
    create_tableau,
    objective_value,
    pivot,
    select_entering_column,
    select_leaving_row,
)


def _basic_values(tableau):
    return [row[-1] for row in tableau]


def _record(form, tableau, basis, costs, reduced_costs, iteration,
            entering=None, leaving=None):
    values = [Fraction(0)] * len(form.objective)
    for row_index, column in enumerate(basis):
        values[column] = tableau[row_index][-1]
    decisions = values[:form.decision_variable_count]
    return {
        "iteration": iteration,
        "basic_variables": [form.variable_names[index] for index in basis],
        "basic_values": _basic_values(tableau),
        "variables": dict(zip(form.variable_names, values)),
        "solution": dict(zip(
            form.variable_names[:form.decision_variable_count], decisions
        )),
        "objective_value": dot(form.original_objective, decisions),
        "big_m_objective": objective_value(costs, basis, tableau),
        "reduced_costs": dict(zip(form.variable_names, reduced_costs)),
        "entering_variable": (
            form.variable_names[entering] if entering is not None else None
        ),
        "leaving_variable": (
            form.variable_names[basis[leaving]] if leaving is not None else None
        ),
    }


def solve_big_m(
    objective,
    matrix,
    rhs,
    senses,
    direction="max",
    max_iterations=1000,
):
    """Solve an LP using the Big-M tableau method with exact rational arithmetic.

    Big M is represented symbolically as ``(coefficient_of_M, constant)``.
    """
    if not isinstance(max_iterations, int) or max_iterations < 1:
        raise ValueError("max_iterations debe ser un entero positivo.")
    form = build_standard_form(objective, matrix, rhs, senses, direction)
    tableau = create_tableau(form)
    basis = form.basis[:]
    iterations = []
    status = "optimal"

    while True:
        reduced_costs, costs = calculate_reduced_costs(form, basis, tableau)
        entering = select_entering_column(reduced_costs)
        if entering is None:
            iterations.append(
                _record(form, tableau, basis, costs, reduced_costs, len(iterations))
            )
            break

        leaving = select_leaving_row(tableau, basis, entering)
        if leaving is None:
            iterations.append(
                _record(
                    form, tableau, basis, costs, reduced_costs, len(iterations),
                    entering,
                )
            )
            artificial_value = sum(
                (
                    tableau[row][-1]
                    for row, column in enumerate(basis)
                    if column in form.artificial_indices
                ),
                Fraction(0),
            )
            status = "infeasible" if artificial_value > 0 else "unbounded"
            break
        if len(iterations) >= max_iterations:
            status = "iteration_limit"
            break

        iterations.append(
            _record(
                form, tableau, basis, costs, reduced_costs, len(iterations),
                entering, leaving,
            )
        )
        pivot(tableau, basis, leaving, entering)

    if status == "optimal":
        artificial_value = sum(
            (
                tableau[row][-1]
                for row, column in enumerate(basis)
                if column in form.artificial_indices
            ),
            Fraction(0),
        )
        if artificial_value > 0:
            status = "infeasible"

    if status != "optimal":
        return {
            "status": status,
            "objective_value": None,
            "solution": None,
            "iterations": iterations,
        }

    values = [Fraction(0)] * len(form.objective)
    for row_index, column in enumerate(basis):
        values[column] = tableau[row_index][-1]
    decisions = values[:form.decision_variable_count]
    return {
        "status": "optimal",
        "objective_value": dot(form.original_objective, decisions),
        "solution": dict(zip(
            form.variable_names[:form.decision_variable_count], decisions
        )),
        "iterations": iterations,
    }