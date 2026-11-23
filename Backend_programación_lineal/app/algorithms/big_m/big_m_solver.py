from fractions import Fraction

from ..common.graphical import compute_graphical_method
from ..common.pivot import compute_ratio_test, dot
from ..common.sensitivity import compute_sensitivity_analysis
from ..common.special_cases import analyze_special_cases
from ..common.standard_form import (
    build_standard_form,
    compute_constraint_results,
    describe_standard_form,
    format_fraction,
)
from .tableau import (
    calculate_reduced_costs,
    create_tableau,
    objective_value,
    pivot,
    select_entering_column,
    select_leaving_row,
)


def _format_big_m(cost: tuple[Fraction, Fraction]) -> str:
    m_coef, const = cost
    if m_coef == 0:
        return format_fraction(const)
    if m_coef == 1:
        m_part = "M"
    elif m_coef == -1:
        m_part = "-M"
    else:
        m_part = f"{format_fraction(m_coef)}M"
    if const == 0:
        return m_part
    if const > 0:
        return f"{m_part} + {format_fraction(const)}"
    return f"{m_part} - {format_fraction(abs(const))}"


def _basic_values(tableau):
    return [row[-1] for row in tableau]


def _record(
    form,
    tableau,
    basis,
    costs,
    reduced_costs,
    iteration,
    entering=None,
    leaving=None,
    entering_reason=None,
    leaving_reason=None,
):
    values = [Fraction(0)] * len(form.objective)
    for row_index, column in enumerate(basis):
        values[column] = tableau[row_index][-1]
    decisions = values[:form.decision_variable_count]
    basic_vals = _basic_values(tableau)

    ratio_test = []
    pivot_info = None
    if entering is not None:
        col_vals = [row[entering] for row in tableau]
        ratio_test = compute_ratio_test(
            col_vals, basic_vals, basis, form.variable_names, leaving_row=leaving
        )
        if leaving is not None:
            pivot_info = {
                "row": leaving,
                "col": entering,
                "row_variable": form.variable_names[basis[leaving]],
                "col_variable": form.variable_names[entering],
                "value": tableau[leaving][entering],
            }

    return {
        "iteration": iteration,
        "basic_variables": [form.variable_names[index] for index in basis],
        "basic_values": basic_vals,
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
        "variable_names": list(form.variable_names),
        "tableau": [row[:] for row in tableau],
        "ratio_test": ratio_test,
        "pivot": pivot_info,
        "entering_reason": entering_reason,
        "leaving_reason": leaving_reason,
        "is_degenerate": any(val == 0 for val in basic_vals),
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
            artificial_value = sum(
                (
                    tableau[row][-1]
                    for row, column in enumerate(basis)
                    if column in form.artificial_indices
                ),
                Fraction(0),
            )
            if artificial_value > 0:
                stop_reason = (
                    "No quedan costos reducidos positivos, pero permanece al menos una variable artificial "
                    "positiva en la base: el problema es infactible."
                )
            else:
                stop_reason = (
                    "Todos los costos reducidos Cj - Zj son ≤ 0: se cumple la condición de optimalidad."
                )
            iterations.append(
                _record(
                    form,
                    tableau,
                    basis,
                    costs,
                    reduced_costs,
                    len(iterations),
                    entering_reason=stop_reason,
                    leaving_reason="No hay cambio de base en esta iteración final.",
                )
            )
            break

        entering_name = form.variable_names[entering]
        entering_rc = _format_big_m(reduced_costs[entering])
        entering_reason = (
            f"Entra {entering_name} porque tiene costo reducido positivo "
            f"(Cj - Zj = {entering_rc} > 0, seleccionada por la regla de Bland)."
        )

        leaving = select_leaving_row(tableau, basis, entering)
        if leaving is None:
            artificial_value = sum(
                (
                    tableau[row][-1]
                    for row, column in enumerate(basis)
                    if column in form.artificial_indices
                ),
                Fraction(0),
            )
            status = "infeasible" if artificial_value > 0 else "unbounded"
            leaving_reason = (
                "Ningún coeficiente de la columna entrante es positivo y permanecen variables artificiales positivas: problema infactible."
                if status == "infeasible"
                else (
                    f"Ningún coeficiente en la columna de {entering_name} es positivo (todos ≤ 0): "
                    f"{entering_name} puede crecer indefinidamente, el problema es no acotado."
                )
            )
            iterations.append(
                _record(
                    form,
                    tableau,
                    basis,
                    costs,
                    reduced_costs,
                    len(iterations),
                    entering,
                    entering_reason=entering_reason,
                    leaving_reason=leaving_reason,
                )
            )
            break

        if len(iterations) >= max_iterations:
            status = "iteration_limit"
            break

        leaving_name = form.variable_names[basis[leaving]]
        rhs_val = tableau[leaving][-1]
        piv_val = tableau[leaving][entering]
        min_ratio = rhs_val / piv_val
        leaving_reason = (
            f"Sale {leaving_name} por la prueba de la razón mínima: "
            f"{format_fraction(rhs_val)} / {format_fraction(piv_val)} = {format_fraction(min_ratio)} "
            f"(elemento pivote = {format_fraction(piv_val)} en fila {leaving + 1})."
        )

        iterations.append(
            _record(
                form,
                tableau,
                basis,
                costs,
                reduced_costs,
                len(iterations),
                entering,
                leaving,
                entering_reason=entering_reason,
                leaving_reason=leaving_reason,
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

    standard_form_desc = describe_standard_form(form, method="big_m")

    if status != "optimal":
        special_cases = analyze_special_cases(
            form, status, None, iterations
        )
        sensitivity = compute_sensitivity_analysis(form, status, None)
        graphical = compute_graphical_method(
            form.original_objective,
            form.original_matrix,
            form.original_rhs,
            form.original_senses,
            form.direction,
            status,
        )
        return {
            "status": status,
            "objective_value": None,
            "solution": None,
            "iterations": iterations,
            "standard_form": standard_form_desc,
            "constraint_results": [],
            "special_cases": special_cases,
            "sensitivity": sensitivity,
            "graphical": graphical,
        }

    values = [Fraction(0)] * len(form.objective)
    for row_index, column in enumerate(basis):
        values[column] = tableau[row_index][-1]
    decisions = values[:form.decision_variable_count]
    opt_val = dot(form.original_objective, decisions)
    opt_sol = dict(zip(
        form.variable_names[:form.decision_variable_count], decisions
    ))
    constraint_results = compute_constraint_results(form, decisions)
    special_cases = analyze_special_cases(
        form,
        status,
        basis,
        iterations,
        optimal_value=opt_val,
        optimal_solution=opt_sol,
    )
    sensitivity = compute_sensitivity_analysis(
        form,
        status,
        basis,
        is_degenerate=special_cases["is_degenerate"],
        has_multiple_optima=special_cases["has_multiple_optima"],
    )
    graphical = compute_graphical_method(
        form.original_objective,
        form.original_matrix,
        form.original_rhs,
        form.original_senses,
        form.direction,
        status,
        optimal_value=opt_val,
        optimal_solution=opt_sol,
    )
    return {
        "status": "optimal",
        "objective_value": opt_val,
        "solution": opt_sol,
        "iterations": iterations,
        "standard_form": standard_form_desc,
        "constraint_results": constraint_results,
        "special_cases": special_cases,
        "sensitivity": sensitivity,
        "graphical": graphical,
    }
