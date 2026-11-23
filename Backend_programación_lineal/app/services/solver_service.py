from fractions import Fraction

from ..algorithms.big_m import solve_big_m
from ..algorithms.common.fractions import to_fraction
from ..algorithms.revised_simplex import solve_revised_simplex
from ..models import Constraint, Problem
from ..schemas import (
    BigMCostResponse,
    CompareResponse,
    ComparisonStepResponse,
    ComparisonSummaryResponse,
    ConstraintResultResponse,
    GraphicalBoundsResponse,
    GraphicalLineResponse,
    GraphicalPointResponse,
    GraphicalResponse,
    GraphicalVertexResponse,
    IterationResponse,
    ObjectiveRangeResponse,
    PivotInfoResponse,
    ProblemRequest,
    RatioTestEntryResponse,
    RhsRangeResponse,
    SensitivityResponse,
    SolveResponse,
    SpecialCasesResponse,
    StandardFormConstraintResponse,
    StandardFormResponse,
)
from .pdf_export import generate_solution_pdf


SOLVERS = {
    "big_m": solve_big_m,
    "revised_simplex": solve_revised_simplex,
}


def _to_domain_problem(request: ProblemRequest) -> Problem:
    constraints = tuple(
        Constraint(
            coefficients=tuple(to_fraction(value) for value in item.coefficients),
            sense=item.sense,
            rhs=to_fraction(item.rhs),
        )
        for item in request.constraints
    )
    return Problem(
        objective=tuple(to_fraction(value) for value in request.objective),
        constraints=constraints,
        direction=request.direction,
        method=request.method,
        max_iterations=request.max_iterations,
    )


def _format_fraction(value: Fraction) -> str:
    value = to_fraction(value)
    if value.denominator == 1:
        return str(value.numerator)
    return "{}/{}".format(value.numerator, value.denominator)


def _format_optional_fraction(value: Fraction | None) -> str | None:
    if value is None:
        return None
    return _format_fraction(value)


def _to_iteration_response(data: dict) -> IterationResponse:
    reduced_costs = {}
    for name, value in data["reduced_costs"].items():
        if isinstance(value, tuple):
            reduced_costs[name] = BigMCostResponse(
                m_coefficient=_format_fraction(value[0]),
                constant=_format_fraction(value[1]),
            )
        else:
            reduced_costs[name] = _format_fraction(value)

    big_m_objective = None
    if data.get("big_m_objective") is not None:
        big_m_objective = BigMCostResponse(
            m_coefficient=_format_fraction(data["big_m_objective"][0]),
            constant=_format_fraction(data["big_m_objective"][1]),
        )

    tableau = None
    if data.get("tableau") is not None:
        tableau = [
            [_format_fraction(val) for val in row]
            for row in data["tableau"]
        ]

    inverse_basis = None
    if data.get("inverse_basis") is not None:
        inverse_basis = [
            [_format_fraction(val) for val in row]
            for row in data["inverse_basis"]
        ]

    dual_values = None
    if data.get("dual_values") is not None:
        dual_values = [_format_fraction(val) for val in data["dual_values"]]

    entering_direction = None
    if data.get("entering_direction") is not None:
        entering_direction = [_format_fraction(val) for val in data["entering_direction"]]

    ratio_test = [
        RatioTestEntryResponse(
            row=entry["row"],
            basic_variable=entry["basic_variable"],
            rhs=_format_fraction(entry["rhs"]),
            pivot_column_value=_format_fraction(entry["pivot_column_value"]),
            ratio=_format_optional_fraction(entry["ratio"]),
            eligible=entry["eligible"],
            is_minimum=entry["is_minimum"],
        )
        for entry in data.get("ratio_test", [])
    ]

    pivot_info = None
    if data.get("pivot") is not None:
        pv = data["pivot"]
        pivot_info = PivotInfoResponse(
            row=pv["row"],
            col=pv["col"],
            row_variable=pv["row_variable"],
            col_variable=pv["col_variable"],
            value=_format_fraction(pv["value"]),
        )

    return IterationResponse(
        iteration=data["iteration"],
        phase=data.get("phase"),
        basic_variables=list(data["basic_variables"]),
        basic_values=[_format_fraction(value) for value in data["basic_values"]],
        variables={
            name: _format_fraction(value)
            for name, value in data["variables"].items()
        },
        solution={
            name: _format_fraction(value)
            for name, value in data["solution"].items()
        },
        objective_value=_format_fraction(data["objective_value"]),
        phase_objective_value=_format_optional_fraction(data.get("phase_objective_value")),
        big_m_objective=big_m_objective,
        reduced_costs=reduced_costs,
        entering_variable=data.get("entering_variable"),
        leaving_variable=data.get("leaving_variable"),
        variable_names=list(data.get("variable_names", [])),
        tableau=tableau,
        inverse_basis=inverse_basis,
        dual_values=dual_values,
        entering_direction=entering_direction,
        ratio_test=ratio_test,
        pivot=pivot_info,
        entering_reason=data.get("entering_reason"),
        leaving_reason=data.get("leaving_reason"),
        is_degenerate=bool(data.get("is_degenerate", False)),
    )


def _to_standard_form_response(data: dict) -> StandardFormResponse:
    return StandardFormResponse(
        direction=data["direction"],
        original_objective=data["original_objective"],
        standard_objective=data["standard_objective"],
        objective_note=data["objective_note"],
        variable_names=list(data["variable_names"]),
        decision_variables=list(data["decision_variables"]),
        slack_variables=list(data["slack_variables"]),
        surplus_variables=list(data["surplus_variables"]),
        artificial_variables=list(data["artificial_variables"]),
        initial_basis=list(data["initial_basis"]),
        constraints=[
            StandardFormConstraintResponse(**c)
            for c in data["constraints"]
        ],
    )


def _to_constraint_results_response(items: list[dict]) -> list[ConstraintResultResponse]:
    return [
        ConstraintResultResponse(
            constraint_index=item["constraint_index"],
            sense=item["sense"],
            lhs_value=_format_fraction(item["lhs_value"]),
            rhs_value=_format_fraction(item["rhs_value"]),
            slack_or_surplus=_format_fraction(item["slack_or_surplus"]),
            type=item["type"],
            variable_name=item.get("variable_name"),
            is_binding=item["is_binding"],
        )
        for item in items
    ]


def _to_special_cases_response(data: dict) -> SpecialCasesResponse:
    return SpecialCasesResponse(
        is_infeasible=data["is_infeasible"],
        is_unbounded=data["is_unbounded"],
        is_degenerate=data["is_degenerate"],
        degenerate_during_iterations=data["degenerate_during_iterations"],
        degenerate_variables=list(data["degenerate_variables"]),
        has_multiple_optima=data["has_multiple_optima"],
        alternative_solutions=[
            {k: _format_fraction(v) for k, v in sol.items()}
            for sol in data.get("alternative_solutions", [])
        ],
        messages=list(data.get("messages", [])),
    )


def _to_sensitivity_response(data: dict) -> SensitivityResponse:
    return SensitivityResponse(
        applicable=data["applicable"],
        message=data["message"],
        objective_ranges=[
            ObjectiveRangeResponse(
                variable=o["variable"],
                optimal_value=_format_fraction(o["optimal_value"]),
                is_basic=o["is_basic"],
                reduced_cost=_format_fraction(o["reduced_cost"]),
                current_coefficient=_format_fraction(o["current_coefficient"]),
                allowable_decrease=_format_optional_fraction(o["allowable_decrease"]),
                allowable_increase=_format_optional_fraction(o["allowable_increase"]),
                min_value=_format_optional_fraction(o["min_value"]),
                max_value=_format_optional_fraction(o["max_value"]),
                interpretation=o["interpretation"],
            )
            for o in data.get("objective_ranges", [])
        ],
        rhs_ranges=[
            RhsRangeResponse(
                constraint_index=r["constraint_index"],
                sense=r["sense"],
                slack_or_surplus=_format_fraction(r["slack_or_surplus"]),
                type=r["type"],
                is_binding=r["is_binding"],
                shadow_price=_format_fraction(r["shadow_price"]),
                current_rhs=_format_fraction(r["current_rhs"]),
                allowable_decrease=_format_optional_fraction(r["allowable_decrease"]),
                allowable_increase=_format_optional_fraction(r["allowable_increase"]),
                min_value=_format_optional_fraction(r["min_value"]),
                max_value=_format_optional_fraction(r["max_value"]),
                interpretation=r["interpretation"],
            )
            for r in data.get("rhs_ranges", [])
        ],
        notes=list(data.get("notes", [])),
    )


def _to_graphical_response(data: dict) -> GraphicalResponse:
    if not data.get("applicable"):
        return GraphicalResponse(
            applicable=False,
            message=data["message"],
        )
    return GraphicalResponse(
        applicable=True,
        message=data["message"],
        region_type=data.get("region_type"),
        bounds=GraphicalBoundsResponse(**data["bounds"]) if data.get("bounds") else None,
        feasible_polygon=[GraphicalPointResponse(**p) for p in data.get("feasible_polygon", [])],
        vertices=[GraphicalVertexResponse(**v) for v in data.get("vertices", [])],
        constraint_lines=[
            GraphicalLineResponse(
                index=ln.get("index"),
                label=ln["label"],
                equation=ln["equation"],
                sense=ln.get("sense"),
                points=[GraphicalPointResponse(**p) for p in ln.get("points", [])],
            )
            for ln in data.get("constraint_lines", [])
        ],
        objective_line=(
            GraphicalLineResponse(
                label=data["objective_line"]["label"],
                equation=data["objective_line"]["equation"],
                points=[GraphicalPointResponse(**p) for p in data["objective_line"]["points"]],
            )
            if data.get("objective_line")
            else None
        ),
        optimal_segment=[GraphicalVertexResponse(**v) for v in data.get("optimal_segment", [])],
    )


def _solve_with_method(
    problem: Problem,
    method: str,
    mode: str = "step_by_step",
) -> SolveResponse:
    matrix = [list(constraint.coefficients) for constraint in problem.constraints]
    rhs = [constraint.rhs for constraint in problem.constraints]
    senses = [constraint.sense for constraint in problem.constraints]
    solver = SOLVERS[method]
    raw_result = solver(
        objective=list(problem.objective),
        matrix=matrix,
        rhs=rhs,
        senses=senses,
        direction=problem.direction,
        max_iterations=problem.max_iterations,
    )

    iterations_list = (
        [_to_iteration_response(item) for item in raw_result["iterations"]]
        if mode == "step_by_step"
        else []
    )

    return SolveResponse(
        status=raw_result["status"],
        method=method,
        mode=mode,
        objective_value=_format_optional_fraction(raw_result["objective_value"]),
        solution=(
            {
                name: _format_fraction(value)
                for name, value in raw_result["solution"].items()
            }
            if raw_result["solution"] is not None
            else None
        ),
        iterations=iterations_list,
        standard_form=_to_standard_form_response(raw_result["standard_form"]),
        constraint_results=_to_constraint_results_response(raw_result.get("constraint_results", [])),
        special_cases=_to_special_cases_response(raw_result["special_cases"]),
        sensitivity=_to_sensitivity_response(raw_result["sensitivity"]),
        graphical=_to_graphical_response(raw_result["graphical"]),
    )


def solve_problem(request: ProblemRequest) -> SolveResponse:
    problem = _to_domain_problem(request)
    return _solve_with_method(problem, request.method, request.mode)


def compare_methods(request: ProblemRequest) -> CompareResponse:
    problem = _to_domain_problem(request)
    bm_res = _solve_with_method(problem, "big_m", "step_by_step")
    rs_res = _solve_with_method(problem, "revised_simplex", "step_by_step")

    bm_count = len(bm_res.iterations)
    rs_count = len(rs_res.iterations)
    rs_p1 = sum(1 for it in rs_res.iterations if it.phase == "I")
    rs_p2 = sum(1 for it in rs_res.iterations if it.phase in ("II", None))

    same_status = bm_res.status == rs_res.status
    same_z = bm_res.objective_value == rs_res.objective_value
    same_sol = bm_res.solution == rs_res.solution

    max_len = max(bm_count, rs_count)
    steps = []
    for idx in range(max_len):
        bm_it = bm_res.iterations[idx] if idx < bm_count else None
        rs_it = rs_res.iterations[idx] if idx < rs_count else None
        steps.append(
            ComparisonStepResponse(
                step=idx,
                big_m_basis=bm_it.basic_variables if bm_it else None,
                big_m_entering=bm_it.entering_variable if bm_it else None,
                big_m_leaving=bm_it.leaving_variable if bm_it else None,
                big_m_z=bm_it.objective_value if bm_it else None,
                revised_phase=rs_it.phase if rs_it else None,
                revised_basis=rs_it.basic_variables if rs_it else None,
                revised_entering=rs_it.entering_variable if rs_it else None,
                revised_leaving=rs_it.leaving_variable if rs_it else None,
                revised_z=rs_it.objective_value if rs_it else None,
            )
        )

    if bm_count < rs_count:
        perf_note = f"Gran M requirió menos iteraciones ({bm_count} vs. {rs_count})."
    elif rs_count < bm_count:
        perf_note = f"Simplex Revisado requirió menos iteraciones ({rs_count} vs. {bm_count})."
    else:
        perf_note = f"Ambos métodos completaron la resolución en exactamente {bm_count} iteraciones."

    consistency_note = (
        "Ambos métodos coinciden exactamente en el estado y resultado."
        if (same_status and same_z)
        else "Los métodos reportaron diferencias que conviene revisar."
    )
    if same_status and same_z and not same_sol and bm_res.special_cases.has_multiple_optima:
        consistency_note = (
            "Ambos métodos alcanzan el mismo Z* óptimo en vértices distintos debido a la existencia de soluciones óptimas múltiples."
        )

    summary = ComparisonSummaryResponse(
        big_m_iterations=bm_count,
        revised_simplex_iterations=rs_count,
        revised_phase1_iterations=rs_p1,
        revised_phase2_iterations=rs_p2,
        same_status=same_status,
        same_objective_value=same_z,
        same_solution=same_sol,
        summary=f"{consistency_note} {perf_note}",
        steps=steps,
    )

    return CompareResponse(
        big_m=bm_res,
        revised_simplex=rs_res,
        comparison=summary,
    )


def export_solution_pdf(request: ProblemRequest) -> bytes:
    problem = _to_domain_problem(request)
    # Always include full step-by-step details in the exported PDF
    response = _solve_with_method(problem, request.method, "step_by_step")
    return generate_solution_pdf(response.model_dump())
