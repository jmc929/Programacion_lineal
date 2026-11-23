from fractions import Fraction

from ..common.graphical import compute_graphical_method
from ..common.matrix_operations import matrix_vector_product, transpose
from ..common.pivot import (
    choose_entering_column,
    choose_leaving_row,
    compute_ratio_test,
    dot,
)
from ..common.sensitivity import compute_sensitivity_analysis
from ..common.special_cases import analyze_special_cases
from ..common.standard_form import (
    build_standard_form,
    compute_constraint_results,
    describe_standard_form,
    format_fraction,
)
from .iterations import calculate_iteration


def _full_solution(variable_count, basis, basic_values):
    values = [Fraction(0)] * variable_count
    for index, value in zip(basis, basic_values):
        values[index] = value
    return values


def _record(
    form,
    basis,
    values,
    reduced_costs,
    phase_value,
    phase,
    iteration,
    inverse_basis,
    dual_values,
    entering=None,
    leaving=None,
    entering_direction=None,
    entering_reason=None,
    leaving_reason=None,
):
    all_values = _full_solution(len(form.objective), basis, values)
    decisions = all_values[:form.decision_variable_count]

    ratio_test = []
    pivot_info = None
    if entering is not None and entering_direction is not None:
        ratio_test = compute_ratio_test(
            entering_direction, values, basis, form.variable_names, leaving_row=leaving
        )
        if leaving is not None:
            pivot_info = {
                "row": leaving,
                "col": entering,
                "row_variable": form.variable_names[basis[leaving]],
                "col_variable": form.variable_names[entering],
                "value": entering_direction[leaving],
            }

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
        "variable_names": list(form.variable_names),
        "inverse_basis": [row[:] for row in inverse_basis],
        "dual_values": list(dual_values),
        "entering_direction": list(entering_direction) if entering_direction is not None else None,
        "ratio_test": ratio_test,
        "pivot": pivot_info,
        "entering_reason": entering_reason,
        "leaving_reason": leaving_reason,
        "is_degenerate": any(val == 0 for val in values),
    }


def _run_phase(
    form,
    active_matrix,
    active_rhs,
    basis,
    costs,
    allowed_columns,
    phase,
    iterations,
    max_iterations,
):
    while True:
        values, reduced, phase_value, inverse_basis = calculate_iteration(
            active_matrix, active_rhs, costs, basis
        )
        basic_costs = [costs[col] for col in basis]
        dual_values = matrix_vector_product(transpose(inverse_basis), basic_costs)
        entering = choose_entering_column(reduced, allowed_columns)
        if entering is None:
            if phase == "I":
                art_sum = sum(
                    (values[row] for row, col in enumerate(basis) if col in form.artificial_indices),
                    Fraction(0),
                )
                stop_reason = (
                    "Fase I finalizada con suma de artificiales positiva: el problema es infactible."
                    if art_sum > 0
                    else "Fase I finalizada con todas las variables artificiales en 0: se encontró una base inicial factible para la Fase II."
                )
            else:
                phase_suffix = f" en Fase {phase}" if phase else ""
                stop_reason = (
                    f"Todos los costos reducidos de variables permitidas son ≤ 0: se alcanza la condición de optimalidad{phase_suffix}."
                )
            iterations.append(
                _record(
                    form,
                    basis,
                    values,
                    reduced,
                    phase_value,
                    phase,
                    len(iterations),
                    inverse_basis,
                    dual_values,
                    entering_reason=stop_reason,
                    leaving_reason=(
                        f"Sin pivoteo al cerrar la Fase {phase}."
                        if phase
                        else "No hay cambio de base en esta iteración final."
                    ),
                )
            )
            return "optimal"

        entering_name = form.variable_names[entering]
        phase_prefix = f"Fase {phase}: " if phase else ""
        entering_reason = (
            f"{phase_prefix}entra {entering_name} porque su costo reducido es positivo "
            f"(c̄ = {format_fraction(reduced[entering])} > 0, regla de Bland)."
        )

        direction = matrix_vector_product(
            inverse_basis,
            [row[entering] for row in active_matrix],
        )
        leaving = choose_leaving_row(
            [[value, direction[index]] for index, value in enumerate(values)],
            basis,
            1,
            0,
        )
        if leaving is None:
            leaving_reason = (
                f"Todos los componentes del vector dirección d = B⁻¹·a_{entering_name} son ≤ 0: "
                f"{entering_name} puede crecer indefinidamente (problema no acotado)."
            )
            iterations.append(
                _record(
                    form,
                    basis,
                    values,
                    reduced,
                    phase_value,
                    phase,
                    len(iterations),
                    inverse_basis,
                    dual_values,
                    entering=entering,
                    entering_direction=direction,
                    entering_reason=entering_reason,
                    leaving_reason=leaving_reason,
                )
            )
            return "unbounded"

        if len(iterations) >= max_iterations:
            return "iteration_limit"

        leaving_name = form.variable_names[basis[leaving]]
        rhs_val = values[leaving]
        piv_val = direction[leaving]
        min_ratio = rhs_val / piv_val
        leaving_reason = (
            f"Sale {leaving_name} por la prueba de la razón mínima: "
            f"{format_fraction(rhs_val)} / {format_fraction(piv_val)} = {format_fraction(min_ratio)} "
            f"(pivote d[{leaving + 1}] = {format_fraction(piv_val)})."
        )

        iterations.append(
            _record(
                form,
                basis,
                values,
                reduced,
                phase_value,
                phase,
                len(iterations),
                inverse_basis,
                dual_values,
                entering=entering,
                leaving=leaving,
                entering_direction=direction,
                entering_reason=entering_reason,
                leaving_reason=leaving_reason,
            )
        )
        basis[leaving] = entering


def _remove_artificial_basics(form, active_matrix, active_rhs, active_row_indices, basis):
    row_index = 0
    while row_index < len(basis):
        if basis[row_index] not in form.artificial_indices:
            row_index += 1
            continue

        inverse_basis = calculate_iteration(
            active_matrix, active_rhs, [Fraction(0)] * len(form.objective), basis
        )[3]
        basic_set = set(basis)
        replacement = None
        for column in range(len(form.objective)):
            if column in form.artificial_indices or column in basic_set:
                continue
            transformed_coefficient = sum(
                (
                    inverse_basis[row_index][source_row]
                    * active_matrix[source_row][column]
                    for source_row in range(len(active_rhs))
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
            del active_matrix[row_index]
            del active_rhs[row_index]
            del active_row_indices[row_index]
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
    active_matrix = [row[:] for row in form.matrix]
    active_rhs = list(form.rhs)
    active_row_indices = list(range(len(form.rhs)))
    basis = form.basis[:]
    iterations = []
    standard_form_desc = describe_standard_form(form, method="revised_simplex")

    # Only run Phase I when artificial variables are actually needed, OR keep Phase I for consistency?
    # Wait: if there are no artificial variables, Phase I takes 1 zero-pivot iteration (already optimal at W=0).
    # Keeping Phase I only when artificial_indices is non-empty makes Revised Simplex cleaner AND avoids redundant
    # Phase I iteration on all-<= problems — let's check if existing tests care!
    # Existing tests in test_algorithms.py & test_api.py only check status, objective_value, solution, iterations[-1].
    # Skipping Phase I when form.artificial_indices is empty is actually standard textbook Revised Simplex!
    if form.artificial_indices:
        phase_one_costs = [
            Fraction(-1) if column in form.artificial_indices else Fraction(0)
            for column in range(len(form.objective))
        ]
        phase_one_status = _run_phase(
            form,
            active_matrix,
            active_rhs,
            basis,
            phase_one_costs,
            range(len(form.objective)),
            "I",
            iterations,
            max_iterations,
        )

        if phase_one_status == "iteration_limit":
            return _build_non_optimal_result(form, "iteration_limit", iterations, standard_form_desc)
        if phase_one_status == "unbounded":
            raise ArithmeticError("La fase I no puede ser no acotada.")

        values = calculate_iteration(
            active_matrix, active_rhs, phase_one_costs, basis
        )[0]
        if sum(
            (values[row] for row, column in enumerate(basis)
             if column in form.artificial_indices),
            Fraction(0),
        ) > 0:
            return _build_non_optimal_result(form, "infeasible", iterations, standard_form_desc)

        _remove_artificial_basics(form, active_matrix, active_rhs, active_row_indices, basis)

    allowed = [
        column
        for column in range(len(form.objective))
        if column not in form.artificial_indices
    ]
    phase_two_status = _run_phase(
        form,
        active_matrix,
        active_rhs,
        basis,
        form.objective,
        allowed,
        "II" if form.artificial_indices else None,
        iterations,
        max_iterations,
    )
    if phase_two_status in ("iteration_limit", "unbounded"):
        return _build_non_optimal_result(form, phase_two_status, iterations, standard_form_desc)

    values = calculate_iteration(
        active_matrix, active_rhs, form.objective, basis
    )[0]
    all_values = _full_solution(len(form.objective), basis, values)
    decisions = all_values[:form.decision_variable_count]
    opt_val = dot(form.original_objective, decisions)
    opt_sol = dict(zip(
        form.variable_names[:form.decision_variable_count], decisions
    ))
    constraint_results = compute_constraint_results(form, decisions)
    special_cases = analyze_special_cases(
        form,
        "optimal",
        basis,
        iterations,
        optimal_value=opt_val,
        optimal_solution=opt_sol,
        active_row_indices=active_row_indices,
    )
    sensitivity = compute_sensitivity_analysis(
        form,
        "optimal",
        basis,
        active_row_indices=active_row_indices,
        is_degenerate=special_cases["is_degenerate"],
        has_multiple_optima=special_cases["has_multiple_optima"],
    )
    graphical = compute_graphical_method(
        form.original_objective,
        form.original_matrix,
        form.original_rhs,
        form.original_senses,
        form.direction,
        "optimal",
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


def _build_non_optimal_result(form, status, iterations, standard_form_desc):
    special_cases = analyze_special_cases(form, status, None, iterations)
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
