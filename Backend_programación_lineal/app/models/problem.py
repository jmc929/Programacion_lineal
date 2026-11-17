from dataclasses import dataclass
from fractions import Fraction
from typing import Literal, TypeAlias


ConstraintSense: TypeAlias = Literal["<=", ">=", "="]
SolverMethod: TypeAlias = Literal["big_m", "revised_simplex"]
Direction: TypeAlias = Literal["max", "min"]
ReducedCost: TypeAlias = Fraction | tuple[Fraction, Fraction]


@dataclass(frozen=True)
class Constraint:
    coefficients: tuple[Fraction, ...]
    sense: ConstraintSense
    rhs: Fraction


@dataclass(frozen=True)
class Problem:
    objective: tuple[Fraction, ...]
    constraints: tuple[Constraint, ...]
    direction: Direction
    method: SolverMethod
    max_iterations: int


@dataclass(frozen=True)
class Iteration:
    iteration: int
    basic_variables: tuple[str, ...]
    basic_values: tuple[Fraction, ...]
    variables: dict[str, Fraction]
    solution: dict[str, Fraction]
    objective_value: Fraction
    reduced_costs: dict[str, ReducedCost]
    entering_variable: str | None
    leaving_variable: str | None
    phase: str | None = None
    phase_objective_value: Fraction | None = None
    big_m_objective: tuple[Fraction, Fraction] | None = None


@dataclass(frozen=True)
class Solution:
    status: Literal["optimal", "infeasible", "unbounded", "iteration_limit"]
    objective_value: Fraction | None
    solution: dict[str, Fraction] | None
    iterations: tuple[Iteration, ...]
