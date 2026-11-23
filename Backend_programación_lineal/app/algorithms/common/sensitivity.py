from fractions import Fraction

from .matrix_operations import inverse, matrix_vector_product, transpose
from .pivot import dot
from .standard_form import StandardForm, format_fraction


def _fmt_bound(value: Fraction | None, neg_inf: bool = False) -> str:
    if value is None:
        return "-∞" if neg_inf else "+∞"
    return format_fraction(value)


def _fmt_delta(value: Fraction | None) -> str:
    if value is None:
        return "∞"
    return format_fraction(value)


def compute_sensitivity_analysis(
    form: StandardForm,
    status: str,
    basis: list[int] | None,
    active_row_indices: list[int] | None = None,
    is_degenerate: bool = False,
    has_multiple_optima: bool = False,
) -> dict:
    """Compute exact sensitivity analysis (shadow prices, reduced costs, c_j and b_i ranges)."""
    if status != "optimal" or basis is None:
        reason_map = {
            "infeasible": "El problema es infactible (no existe región factible), por lo que no aplica el análisis de sensibilidad.",
            "unbounded": "El problema es no acotado (Z crece/decrece indefinidamente), por lo que no aplica el análisis de sensibilidad.",
            "iteration_limit": "Se alcanzó el límite máximo de iteraciones sin llegar a un óptimo confirmado.",
        }
        return {
            "applicable": False,
            "message": reason_map.get(
                status,
                "El análisis de sensibilidad solo aplica cuando existe una solución óptima finita.",
            ),
            "objective_ranges": [],
            "rhs_ranges": [],
            "notes": [],
        }

    m_orig = len(form.original_rhs)
    if active_row_indices is None:
        active_row_indices = list(range(m_orig))

    # Build the active A_std matrix and b_std vector
    active_matrix = [form.matrix[i] for i in active_row_indices]
    active_rhs = [form.rhs[i] for i in active_row_indices]
    m_active = len(active_row_indices)
    n_total = len(form.objective)
    sigma = form.objective_factor  # +1 for max, -1 for min

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

    # Full optimal values for all variables
    all_values = [Fraction(0)] * n_total
    for row_pos, col in enumerate(basis):
        all_values[col] = x_b[row_pos]

    # Reduced costs in standardized max form: c_j - y_std^T * A_j <= 0
    rc_max = []
    for col in range(n_total):
        col_vec = [row[col] for row in active_matrix]
        rc_max.append(form.objective[col] - dot(y_std, col_vec))

    basis_pos = {col: row_pos for row_pos, col in enumerate(basis)}
    non_basic_non_art = [
        col
        for col in range(n_total)
        if col not in basis_pos and col not in form.artificial_indices
    ]

    # 1. Objective coefficient ranges & reduced costs for decision variables
    objective_ranges = []
    for k in range(form.decision_variable_count):
        var_name = form.variable_names[k]
        c_curr = form.original_objective[k]
        val_opt = all_values[k]
        rc_orig = sigma * rc_max[k]
        is_basic = k in basis_pos

        if not is_basic:
            # Non-basic variable: rc_max[k] + delta_k <= 0  =>  delta_k <= -rc_max[k]
            if sigma == 1:
                orig_min_delta = None
                orig_max_delta = -rc_max[k]
            else:
                orig_min_delta = rc_max[k]
                orig_max_delta = None
        else:
            row_r = basis_pos[k]
            b_inv_row = b_inv[row_r]
            delta_min = None
            delta_max = None
            for j in non_basic_non_art:
                col_j = [row[j] for row in active_matrix]
                a_bar_rj = dot(b_inv_row, col_j)
                if a_bar_rj > 0:
                    bound = rc_max[j] / a_bar_rj
                    if delta_min is None or bound > delta_min:
                        delta_min = bound
                elif a_bar_rj < 0:
                    bound = rc_max[j] / a_bar_rj
                    if delta_max is None or bound < delta_max:
                        delta_max = bound

            if sigma == 1:
                orig_min_delta = delta_min
                orig_max_delta = delta_max
            else:
                orig_min_delta = (-delta_max) if delta_max is not None else None
                orig_max_delta = (-delta_min) if delta_min is not None else None

        min_val = (c_curr + orig_min_delta) if orig_min_delta is not None else None
        max_val = (c_curr + orig_max_delta) if orig_max_delta is not None else None
        allow_dec = (-orig_min_delta) if orig_min_delta is not None else None
        allow_inc = orig_max_delta

        # Human-readable interpretation
        if is_basic:
            interp = (
                f"{var_name} es básica (valor = {format_fraction(val_opt)}, costo reducido = 0). "
                f"Su coeficiente puede variar en [{_fmt_bound(min_val, True)}, {_fmt_bound(max_val, False)}] "
                f"sin cambiar la base óptima actual."
            )
        else:
            if rc_orig == 0:
                interp = (
                    f"{var_name} es no básica con costo reducido 0 (indica posibles óptimos múltiples). "
                    f"Su coeficiente mantiene la base actual en [{_fmt_bound(min_val, True)}, {_fmt_bound(max_val, False)}]."
                )
            elif form.direction == "max":
                interp = (
                    f"{var_name} es no básica (valor = 0). Su costo reducido es {format_fraction(rc_orig)}: "
                    f"forzar 1 unidad de {var_name} reduciría Z en {format_fraction(abs(rc_orig))}. "
                    f"Su coeficiente debería aumentar al menos en {format_fraction(abs(rc_orig))} "
                    f"(hasta {format_fraction(max_val)}) para que convenga producirla."
                )
            else:
                interp = (
                    f"{var_name} es no básica (valor = 0). Su costo reducido es {format_fraction(rc_orig)}: "
                    f"forzar 1 unidad de {var_name} aumentaría el costo Z en {format_fraction(abs(rc_orig))}. "
                    f"Su coeficiente debería disminuir al menos en {format_fraction(abs(rc_orig))} "
                    f"(hasta {format_fraction(min_val)}) para que convenga incluirla."
                )

        objective_ranges.append(
            {
                "variable": var_name,
                "optimal_value": val_opt,
                "is_basic": is_basic,
                "reduced_cost": rc_orig,
                "current_coefficient": c_curr,
                "allowable_decrease": allow_dec,
                "allowable_increase": allow_inc,
                "min_value": min_val,
                "max_value": max_val,
                "interpretation": interp,
            }
        )

    # 2. Shadow prices and RHS ranges for every original constraint
    active_pos_map = {orig_idx: pos for pos, orig_idx in enumerate(active_row_indices)}
    decision_vals = all_values[:form.decision_variable_count]
    rhs_ranges = []

    for orig_idx in range(m_orig):
        meta = form.constraint_metadata[orig_idx]
        b_curr = form.original_rhs[orig_idx]
        lhs_val = sum(
            (a * x for a, x in zip(form.original_matrix[orig_idx], decision_vals)),
            Fraction(0),
        )
        if meta.original_sense == "<=":
            slack_surplus = b_curr - lhs_val
            ctype = "holgura"
        elif meta.original_sense == ">=":
            slack_surplus = lhs_val - b_curr
            ctype = "exceso"
        else:
            slack_surplus = Fraction(0)
            ctype = "igualdad"

        is_binding = slack_surplus == 0

        if orig_idx not in active_pos_map:
            # Redundant equality row removed during Phase I cleanup
            rhs_ranges.append(
                {
                    "constraint_index": meta.index,
                    "sense": meta.original_sense,
                    "slack_or_surplus": slack_surplus,
                    "type": ctype,
                    "is_binding": True,
                    "shadow_price": Fraction(0),
                    "current_rhs": b_curr,
                    "allowable_decrease": Fraction(0),
                    "allowable_increase": Fraction(0),
                    "min_value": b_curr,
                    "max_value": b_curr,
                    "interpretation": (
                        f"R{meta.index} es una restricción de igualdad linealmente redundante; "
                        f"cualquier modificación en su lado derecho ({format_fraction(b_curr)}) rompería la consistencia del sistema."
                    ),
                }
            )
            continue

        row_pos = active_pos_map[orig_idx]
        flip_factor = Fraction(-1) if form.row_flipped[orig_idx] else Fraction(1)
        shadow_price = sigma * flip_factor * y_std[row_pos]

        # x_B + delta_std * (B^-1)[:, row_pos] >= 0
        delta_min = None
        delta_max = None
        for r in range(m_active):
            u_r = b_inv[r][row_pos]
            if u_r > 0:
                bound = -x_b[r] / u_r
                if delta_min is None or bound > delta_min:
                    delta_min = bound
            elif u_r < 0:
                bound = -x_b[r] / u_r
                if delta_max is None or bound < delta_max:
                    delta_max = bound

        if flip_factor == 1:
            orig_min_delta = delta_min
            orig_max_delta = delta_max
        else:
            orig_min_delta = (-delta_max) if delta_max is not None else None
            orig_max_delta = (-delta_min) if delta_min is not None else None

        min_val = (b_curr + orig_min_delta) if orig_min_delta is not None else None
        max_val = (b_curr + orig_max_delta) if orig_max_delta is not None else None
        allow_dec = (-orig_min_delta) if orig_min_delta is not None else None
        allow_inc = orig_max_delta

        if shadow_price == 0:
            if not is_binding:
                interp = (
                    f"R{meta.index} es no activa ({ctype} = {format_fraction(slack_surplus)}). "
                    f"Su precio sombra es 0: variar el lado derecho dentro de "
                    f"[{_fmt_bound(min_val, True)}, {_fmt_bound(max_val, False)}] no cambia el valor óptimo de Z."
                )
            else:
                interp = (
                    f"R{meta.index} es activa pero tiene precio sombra 0 (posible degeneración o restricción redundante). "
                    f"Rango de factibilidad: [{_fmt_bound(min_val, True)}, {_fmt_bound(max_val, False)}]."
                )
        else:
            verb = "aumenta" if shadow_price > 0 else "disminuye"
            interp = (
                f"R{meta.index} es activa (saturada). Su precio sombra es {format_fraction(shadow_price)}: "
                f"por cada unidad adicional en el lado derecho, Z {verb} en {format_fraction(abs(shadow_price))}, "
                f"siempre que b{meta.index} permanezca en [{_fmt_bound(min_val, True)}, {_fmt_bound(max_val, False)}]."
            )

        rhs_ranges.append(
            {
                "constraint_index": meta.index,
                "sense": meta.original_sense,
                "slack_or_surplus": slack_surplus,
                "type": ctype,
                "is_binding": is_binding,
                "shadow_price": shadow_price,
                "current_rhs": b_curr,
                "allowable_decrease": allow_dec,
                "allowable_increase": allow_inc,
                "min_value": min_val,
                "max_value": max_val,
                "interpretation": interp,
            }
        )

    notes = []
    if is_degenerate:
        notes.append(
            "Nota sobre degeneración: al existir una variable básica igual a 0 en el óptimo, "
            "los precios sombra y algunos rangos del lado derecho pueden ser válidos solo en una dirección."
        )
    if has_multiple_optima:
        notes.append(
            "Nota sobre óptimos múltiples: existe al menos una variable no básica con costo reducido 0; "
            "algunos rangos de coeficientes tienen amplitud 0 en un extremo."
        )
    if any(col in form.artificial_indices for col in basis):
        notes.append(
            "Nota: una variable artificial permanece en la base con valor 0 debido a una restricción redundante."
        )

    return {
        "applicable": True,
        "message": "Análisis de sensibilidad calculado con aritmética racional exacta a partir de la base óptima.",
        "objective_ranges": objective_ranges,
        "rhs_ranges": rhs_ranges,
        "notes": notes,
    }
