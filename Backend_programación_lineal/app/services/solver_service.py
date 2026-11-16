from fractions import Fraction

from ..algorithms.big_m import solve_big_m
from ..algorithms.common.fractions import to_fraction
from ..algorithms.revised_simplex import solve_revised_simplex
from ..models import Constraint, Iteration, Problem, Solution
from ..schemas import (
    BigMCostResponse,
    IterationResponse,
    ProblemRequest,
    SolveResponse,
)


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


def _to_domain_iteration(data: dict) -> Iteration:
    reduced_costs = {}
    for name, value in data["reduced_costs"].items():
        if isinstance(value, tuple):
            reduced_costs[name] = (
                to_fraction(value[0]),
                to_fraction(value[1]),
            )
        else:
            reduced_costs[name] = to_fraction(value)

    big_m_objective = data.get("big_m_objective")
    if big_m_objective is not None:
        big_m_objective = (
            to_fraction(big_m_objective[0]),
            to_fraction(big_m_objective[1]),
        )

    return Iteration(
        iteration=data["iteration"],
        phase=data.get("phase"),
        basic_variables=tuple(data["basic_variables"]),
        basic_values=tuple(to_fraction(value) for value in data["basic_values"]),
        variables={
            name: to_fraction(value)
            for name, value in data["variables"].items()
        },
        solution={
            name: to_fraction(value)
            for name, value in data["solution"].items()
        },
        objective_value=to_fraction(data["objective_value"]),
        phase_objective_value=(
            to_fraction(data["phase_objective_value"])
            if data.get("phase_objective_value") is not None
            else None
        ),
        big_m_objective=big_m_objective,
        reduced_costs=reduced_costs,
        entering_variable=data.get("entering_variable"),
        leaving_variable=data.get("leaving_variable"),
    )


def _format_fraction(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return "{}/{}".format(value.numerator, value.denominator)


def _to_iteration_response(iteration: Iteration) -> IterationResponse:
    reduced_costs = {}
    for name, value in iteration.reduced_costs.items():
        if isinstance(value, tuple):
            reduced_costs[name] = BigMCostResponse(
                m_coefficient=_format_fraction(value[0]),
                constant=_format_fraction(value[1]),
            )
        else:
            reduced_costs[name] = _format_fraction(value)

    big_m_objective = None
    if iteration.big_m_objective is not None:
        big_m_objective = BigMCostResponse(
            m_coefficient=_format_fraction(iteration.big_m_objective[0]),
            constant=_format_fraction(iteration.big_m_objective[1]),
        )

    return IterationResponse(
        iteration=iteration.iteration,
        phase=iteration.phase,
        basic_variables=list(iteration.basic_variables),
        basic_values=[_format_fraction(value) for value in iteration.basic_values],
        variables={
            name: _format_fraction(value)
            for name, value in iteration.variables.items()
        },
        solution={
            name: _format_fraction(value)
            for name, value in iteration.solution.items()
        },
        objective_value=_format_fraction(iteration.objective_value),
        phase_objective_value=(
            _format_fraction(iteration.phase_objective_value)
            if iteration.phase_objective_value is not None
            else None
        ),
        big_m_objective=big_m_objective,
        reduced_costs=reduced_costs,
        entering_variable=iteration.entering_variable,
        leaving_variable=iteration.leaving_variable,
    )


def solve_problem(request: ProblemRequest) -> SolveResponse:
    problem = _to_domain_problem(request)
    matrix = [list(constraint.coefficients) for constraint in problem.constraints]
    rhs = [constraint.rhs for constraint in problem.constraints]
    senses = [constraint.sense for constraint in problem.constraints]
    solver = SOLVERS[problem.method]
    raw_result = solver(
        objective=list(problem.objective),
        matrix=matrix,
        rhs=rhs,
        senses=senses,
        direction=problem.direction,
        max_iterations=problem.max_iterations,
    )

    solution = Solution(
        status=raw_result["status"],
        objective_value=(
            to_fraction(raw_result["objective_value"])
            if raw_result["objective_value"] is not None
            else None
        ),
        solution=(
            {
                name: to_fraction(value)
                for name, value in raw_result["solution"].items()
            }
            if raw_result["solution"] is not None
            else None
        ),
        iterations=tuple(
            _to_domain_iteration(item) for item in raw_result["iterations"]
        ),
    )
    return SolveResponse(
        status=solution.status,
        objective_value=(
            _format_fraction(solution.objective_value)
            if solution.objective_value is not None
            else None
        ),
        solution=(
            {
                name: _format_fraction(value)
                for name, value in solution.solution.items()
            }
            if solution.solution is not None
            else None
        ),
        iterations=[
            _to_iteration_response(item) for item in solution.iterations
        ],
    )
