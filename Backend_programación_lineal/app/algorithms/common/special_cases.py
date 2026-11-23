from fractions import Fraction

from .matrix_operations import inverse, matrix_vector_product, transpose
from .pivot import choose_leaving_row, dot
from .standard_form import StandardForm, format_fraction


def _format_point(decision_names: list[str], values: list[Fraction]) -> str:
    coords = ", ".join(format_fraction(v) for v in values)
    return f"({coords})"


def analyze_special_cases(
    form: StandardForm,
    status: str,
    basis: list[int] | None,
    iterations: list[dict],
    optimal_value: Fraction | None = None,
    optimal_solution: dict | None = None,
    active_row_indices: list[int] | None = None,
) -> dict:
    """Detect and explain special LP cases: infeasible, unbounded, multiple optima, degeneracy."""
    messages = []
    decision_names = form.variable_names[:form.decision_variable_count]

    if status == "infeasible":
        messages.append(
            "Problema infactible: no existe solución que satisfaga simultáneamente todas las restricciones "
            "(permanecen variables artificiales positivas en la base)."
        )
        return {
            "is_infeasible": True,
            "is_unbounded": False,
            "is_degenerate": False,
            "degenerate_during_iterations": any(it.get("is_degenerate", False) for it in iterations),
            "degenerate_variables": [],
            "has_multiple_optima": False,
            "alternative_solutions": [],
            "messages": messages,
        }

    if status == "unbounded":
        messages.append(
            "Problema no acotado: la función objetivo puede mejorar indefinidamente sin violar ninguna restricción "
            "(existe una variable entrante sin coeficientes positivos en su columna pivote)."
        )
        return {
            "is_infeasible": False,
            "is_unbounded": True,
            "is_degenerate": False,
            "degenerate_during_iterations": any(it.get("is_degenerate", False) for it in iterations),
            "degenerate_variables": [],
            "has_multiple_optima": False,
            "alternative_solutions": [],
            "messages": messages,
        }

    if status != "optimal" or basis is None or optimal_solution is None:
        messages.append(
            "Se alcanzó el límite máximo de iteraciones antes de confirmar una solución óptima."
        )
        return {
            "is_infeasible": False,
            "is_unbounded": False,
            "is_degenerate": False,
            "degenerate_during_iterations": any(it.get("is_degenerate", False) for it in iterations),
            "degenerate_variables": [],
            "has_multiple_optima": False,
            "alternative_solutions": [],
            "messages": messages,
        }

    m_orig = len(form.original_rhs)
    if active_row_indices is None:
        active_row_indices = list(range(m_orig))

    active_matrix = [form.matrix[i] for i in active_row_indices]
    active_rhs = [form.rhs[i] for i in active_row_indices]
    m_active = len(active_row_indices)
    n_total = len(form.objective)

    if m_active == 0:
        b_inv = []
        x_b = []
        y_std = []
    else:
        basis_mat = [[row[col] for col in basis] for row in active_matrix]
        b_inv = inverse(basis_mat)
        x_b = matrix_vector_product(b_inv, active_rhs)
        c_b = [form.objective[col] for col in basis]
        y_std = matrix_vector_product(transpose(b_inv), c_b)

    # 1. Degeneracy check
    degenerate_vars = [
        form.variable_names[col]
        for col, val in zip(basis, x_b)
        if val == 0
    ]
    is_degenerate = len(degenerate_vars) > 0
    degenerate_during = any(it.get("is_degenerate", False) for it in iterations)

    if is_degenerate:
        vars_str = ", ".join(degenerate_vars)
        messages.append(
            f"Solución óptima degenerada: al menos una variable básica vale 0 en el óptimo ({vars_str} = 0)."
        )
    elif degenerate_during:
        messages.append(
            "Se presentó degeneración en alguna iteración intermedia, aunque la base óptima final no es degenerada."
        )

    # 2. Multiple optimal solutions check
    basis_set = set(basis)
    rc_max = []
    for col in range(n_total):
        col_vec = [row[col] for row in active_matrix]
        rc_max.append(form.objective[col] - dot(y_std, col_vec))

    optimal_decisions = [optimal_solution[name] for name in decision_names]
    alternative_solutions = []
    seen_decision_tuples = {tuple(optimal_decisions)}
    has_unbounded_optimal_ray = False

    zero_rc_nonbasics = [
        col
        for col in range(n_total)
        if col not in basis_set
        and col not in form.artificial_indices
        and rc_max[col] == 0
    ]

    for entering_col in zero_rc_nonbasics:
        if m_active == 0:
            has_unbounded_optimal_ray = True
            continue
        col_vec = [row[entering_col] for row in active_matrix]
        direction = matrix_vector_product(b_inv, col_vec)
        leaving = choose_leaving_row(
            [[x_b[r], direction[r]] for r in range(m_active)],
            basis,
            1,
            0,
        )
        if leaving is None:
            # Increasing entering_col keeps Z optimal forever without leaving feasible region
            # Verify whether decision variables actually change along this ray
            ray_changes_decision = entering_col < form.decision_variable_count or any(
                basis[r] < form.decision_variable_count and direction[r] != 0
                for r in range(m_active)
            )
            if ray_changes_decision:
                has_unbounded_optimal_ray = True
            continue

        theta = x_b[leaving] / direction[leaving]
        if theta > 0:
            new_vals = [Fraction(0)] * n_total
            new_vals[entering_col] = theta
            for r in range(m_active):
                if r != leaving:
                    new_vals[basis[r]] = x_b[r] - theta * direction[r]
            alt_decisions = new_vals[:form.decision_variable_count]
            alt_tuple = tuple(alt_decisions)
            if alt_tuple not in seen_decision_tuples:
                seen_decision_tuples.add(alt_tuple)
                alternative_solutions.append(dict(zip(decision_names, alt_decisions)))

    has_multiple_optima = len(alternative_solutions) > 0 or has_unbounded_optimal_ray

    if has_multiple_optima:
        p1 = _format_point(decision_names, optimal_decisions)
        z_str = format_fraction(optimal_value) if optimal_value is not None else ""
        if alternative_solutions:
            alt_pts = [
                _format_point(decision_names, [alt[name] for name in decision_names])
                for alt in alternative_solutions
            ]
            messages.append(
                f"Soluciones óptimas múltiples: existe una variable no básica con costo reducido igual a 0. "
                f"Z = {z_str} se alcanza en {p1} y también en {', '.join(alt_pts)} "
                f"(y en toda combinación convexa / segmento entre ellos)."
            )
        else:
            messages.append(
                f"Soluciones óptimas múltiples: Z = {z_str} se mantiene constante a lo largo de una semirrecta óptima a partir de {p1}."
            )

    return {
        "is_infeasible": False,
        "is_unbounded": False,
        "is_degenerate": is_degenerate,
        "degenerate_during_iterations": degenerate_during,
        "degenerate_variables": degenerate_vars,
        "has_multiple_optima": has_multiple_optima,
        "alternative_solutions": alternative_solutions,
        "messages": messages,
    }
