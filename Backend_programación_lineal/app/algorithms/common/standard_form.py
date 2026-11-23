from dataclasses import dataclass, field
from fractions import Fraction

from .fractions import to_fraction


def format_fraction(value: Fraction) -> str:
    value = to_fraction(value)
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _format_linear_combination(coefficients, names) -> str:
    terms = []
    for coeff, name in zip(coefficients, names):
        if coeff == 0:
            continue
        abs_coeff = abs(coeff)
        coeff_str = "" if abs_coeff == 1 else format_fraction(abs_coeff)
        if not terms:
            sign = "-" if coeff < 0 else ""
            terms.append(f"{sign}{coeff_str}{name}")
        else:
            sign = " - " if coeff < 0 else " + "
            terms.append(f"{sign}{coeff_str}{name}")
    return "".join(terms) if terms else "0"


@dataclass
class ConstraintMetadata:
    index: int
    original_sense: str
    normalized_sense: str
    flipped: bool
    slack_variable: str | None = None
    slack_column: int | None = None
    slack_type: str = "equality"  # "slack", "surplus", "equality"
    artificial_variable: str | None = None
    artificial_column: int | None = None


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
    direction: str = "max"
    original_matrix: list = field(default_factory=list)
    original_rhs: list = field(default_factory=list)
    original_senses: list = field(default_factory=list)
    normalized_senses: list = field(default_factory=list)
    row_flipped: list = field(default_factory=list)
    constraint_metadata: list = field(default_factory=list)


def build_standard_form(objective, matrix, rhs, senses, direction="max"):
    """Normalize an LP and create an initial feasible basis."""
    objective = [to_fraction(value) for value in objective]
    original_rhs = [to_fraction(value) for value in rhs]
    rhs = list(original_rhs)
    if not objective:
        raise ValueError("Debe existir al menos una variable de decisión.")
    if direction not in ("max", "min"):
        raise ValueError("direction debe ser 'max' o 'min'.")
    if len(matrix) != len(rhs) or len(rhs) != len(senses):
        raise ValueError("A, b y senses deben tener el mismo número de restricciones.")
    if any(len(row) != len(objective) for row in matrix):
        raise ValueError("Cada fila de A debe tener una entrada por variable.")

    original_matrix = [[to_fraction(value) for value in row] for row in matrix]
    normalized_matrix = [row[:] for row in original_matrix]
    original_senses = list(senses)
    normalized_senses = list(senses)
    row_flipped = [False] * len(rhs)

    for row_index, value in enumerate(rhs):
        if normalized_senses[row_index] not in ("<=", ">=", "="):
            raise ValueError("Cada restricción debe usar '<=', '>=' o '='.")
        if value < 0:
            row_flipped[row_index] = True
            rhs[row_index] = -value
            normalized_matrix[row_index] = [
                -coefficient for coefficient in normalized_matrix[row_index]
            ]
            normalized_senses[row_index] = {
                "<=": ">=",
                ">=": "<=",
                "=": "=",
            }[normalized_senses[row_index]]

    variable_names = [f"x{index + 1}" for index in range(len(objective))]
    basis = [None] * len(rhs)
    artificial_indices = set()
    constraint_metadata = []
    next_column = len(objective)

    for row_index, sense in enumerate(normalized_senses):
        meta = ConstraintMetadata(
            index=row_index + 1,
            original_sense=original_senses[row_index],
            normalized_sense=sense,
            flipped=row_flipped[row_index],
        )
        if sense == "<=":
            for row in normalized_matrix:
                row.append(Fraction(0))
            normalized_matrix[row_index][next_column] = Fraction(1)
            basis[row_index] = next_column
            slack_name = f"s{row_index + 1}"
            variable_names.append(slack_name)
            meta.slack_variable = slack_name
            meta.slack_column = next_column
            meta.slack_type = "slack"
            next_column += 1
        elif sense == ">=":
            for row in normalized_matrix:
                row.append(Fraction(0))
            normalized_matrix[row_index][next_column] = Fraction(-1)
            surplus_name = f"e{row_index + 1}"
            variable_names.append(surplus_name)
            meta.slack_variable = surplus_name
            meta.slack_column = next_column
            meta.slack_type = "surplus"
            next_column += 1

            for row in normalized_matrix:
                row.append(Fraction(0))
            normalized_matrix[row_index][next_column] = Fraction(1)
            basis[row_index] = next_column
            artificial_indices.add(next_column)
            art_name = f"a{row_index + 1}"
            variable_names.append(art_name)
            meta.artificial_variable = art_name
            meta.artificial_column = next_column
            next_column += 1
        else:
            for row in normalized_matrix:
                row.append(Fraction(0))
            normalized_matrix[row_index][next_column] = Fraction(1)
            basis[row_index] = next_column
            artificial_indices.add(next_column)
            art_name = f"a{row_index + 1}"
            variable_names.append(art_name)
            meta.slack_type = "equality"
            meta.artificial_variable = art_name
            meta.artificial_column = next_column
            next_column += 1

        constraint_metadata.append(meta)

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
        direction=direction,
        original_matrix=original_matrix,
        original_rhs=original_rhs,
        original_senses=original_senses,
        normalized_senses=normalized_senses,
        row_flipped=row_flipped,
        constraint_metadata=constraint_metadata,
    )


def describe_standard_form(form: StandardForm, method: str = "big_m") -> dict:
    """Build a human-readable structured representation of the standard form."""
    sense_symbol = {"<=": "≤", ">=": "≥", "=": "="}
    decision_names = form.variable_names[:form.decision_variable_count]
    slack_vars = [
        m.slack_variable
        for m in form.constraint_metadata
        if m.slack_type == "slack" and m.slack_variable
    ]
    surplus_vars = [
        m.slack_variable
        for m in form.constraint_metadata
        if m.slack_type == "surplus" and m.slack_variable
    ]
    artificial_vars = [
        m.artificial_variable
        for m in form.constraint_metadata
        if m.artificial_variable
    ]

    orig_obj_expr = _format_linear_combination(form.original_objective, decision_names)
    orig_dir_label = "Max" if form.direction == "max" else "Min"
    original_objective_str = f"{orig_dir_label} Z = {orig_obj_expr}"

    std_obj_expr = _format_linear_combination(form.objective, form.variable_names)
    if method == "big_m" and artificial_vars:
        penalty = "".join(f" - M·{v}" for v in artificial_vars)
        if form.direction == "min":
            standard_objective_str = f"Max Z' = {std_obj_expr}{penalty}  (donde Z' = -Z)"
        else:
            standard_objective_str = f"Max Z = {std_obj_expr}{penalty}"
    elif method == "revised_simplex" and artificial_vars:
        phase1_expr = " - ".join(artificial_vars)
        if form.direction == "min":
            standard_objective_str = (
                f"Fase I: Max W = -{phase1_expr}  |  "
                f"Fase II: Max Z' = {std_obj_expr}  (donde Z' = -Z)"
            )
        else:
            standard_objective_str = (
                f"Fase I: Max W = -{phase1_expr}  |  "
                f"Fase II: Max Z = {std_obj_expr}"
            )
    else:
        if form.direction == "min":
            standard_objective_str = f"Max Z' = {std_obj_expr}  (donde Z' = -Z)"
        else:
            standard_objective_str = f"Max Z = {std_obj_expr}"

    objective_note = (
        "Como el problema es de minimización, se transforma a maximización multiplicando la función objetivo por -1 (Max Z' = -Z)."
        if form.direction == "min"
        else "El problema ya está expresado como maximización."
    )

    constraints_desc = []
    for row_idx, meta in enumerate(form.constraint_metadata):
        orig_lhs = _format_linear_combination(form.original_matrix[row_idx], decision_names)
        orig_eq = f"{orig_lhs} {sense_symbol[meta.original_sense]} {format_fraction(form.original_rhs[row_idx])}"
        std_lhs = _format_linear_combination(form.matrix[row_idx], form.variable_names)
        std_eq = f"{std_lhs} = {format_fraction(form.rhs[row_idx])}"

        notes = []
        added = []
        if meta.flipped:
            notes.append(
                f"Lado derecho negativo ({format_fraction(form.original_rhs[row_idx])}): "
                f"se multiplicó por -1 cambiando el sentido a {sense_symbol[meta.normalized_sense]}."
            )
        if meta.slack_type == "slack" and meta.slack_variable:
            notes.append(f"Se agregó variable de holgura +{meta.slack_variable}.")
            added.append(meta.slack_variable)
        elif meta.slack_type == "surplus" and meta.slack_variable:
            notes.append(
                f"Se restó variable de exceso -{meta.slack_variable} y se agregó variable artificial +{meta.artificial_variable}."
            )
            added.extend([meta.slack_variable, meta.artificial_variable])
        elif meta.artificial_variable:
            notes.append(f"Restricción de igualdad: se agregó variable artificial +{meta.artificial_variable}.")
            added.append(meta.artificial_variable)

        constraints_desc.append(
            {
                "index": meta.index,
                "original_equation": orig_eq,
                "standard_equation": std_eq,
                "flipped": meta.flipped,
                "added_variables": added,
                "note": " ".join(notes),
            }
        )

    return {
        "direction": form.direction,
        "original_objective": original_objective_str,
        "standard_objective": standard_objective_str,
        "objective_note": objective_note,
        "variable_names": list(form.variable_names),
        "decision_variables": list(decision_names),
        "slack_variables": slack_vars,
        "surplus_variables": surplus_vars,
        "artificial_variables": artificial_vars,
        "initial_basis": [form.variable_names[idx] for idx in form.basis],
        "constraints": constraints_desc,
    }


def compute_constraint_results(form: StandardForm, decision_values: list) -> list:
    """Compute LHS evaluation, slack/surplus, and binding status for every original constraint."""
    results = []
    for row_idx, meta in enumerate(form.constraint_metadata):
        lhs_val = sum(
            (a * x for a, x in zip(form.original_matrix[row_idx], decision_values)),
            Fraction(0),
        )
        rhs_val = form.original_rhs[row_idx]
        if meta.original_sense == "<=":
            slack_or_surplus = rhs_val - lhs_val
            ctype = "holgura"
        elif meta.original_sense == ">=":
            slack_or_surplus = lhs_val - rhs_val
            ctype = "exceso"
        else:
            slack_or_surplus = Fraction(0)
            ctype = "igualdad"

        results.append(
            {
                "constraint_index": meta.index,
                "sense": meta.original_sense,
                "lhs_value": lhs_val,
                "rhs_value": rhs_val,
                "slack_or_surplus": slack_or_surplus,
                "type": ctype,
                "variable_name": meta.slack_variable,
                "is_binding": slack_or_surplus == 0,
            }
        )
    return results
