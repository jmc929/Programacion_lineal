from typing import Literal

from pydantic import BaseModel, ConfigDict


class BigMCostResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    m_coefficient: str
    constant: str


class IterationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    iteration: int
    phase: Literal["I", "II"] | None = None
    basic_variables: list[str]
    basic_values: list[str]
    variables: dict[str, str]
    solution: dict[str, str]
    objective_value: str
    phase_objective_value: str | None = None
    big_m_objective: BigMCostResponse | None = None
    reduced_costs: dict[str, str | BigMCostResponse]
    entering_variable: str | None = None
    leaving_variable: str | None = None


class SolveResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["optimal", "infeasible", "unbounded", "iteration_limit"]
    objective_value: str | None
    solution: dict[str, str] | None
    iterations: list[IterationResponse]
