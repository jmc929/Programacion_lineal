from typing import Literal

from pydantic import BaseModel, ConfigDict


class BigMCostResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    m_coefficient: str
    constant: str


class RatioTestEntryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    row: int
    basic_variable: str
    rhs: str
    pivot_column_value: str
    ratio: str | None = None
    eligible: bool
    is_minimum: bool


class PivotInfoResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    row: int
    col: int
    row_variable: str
    col_variable: str
    value: str


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
    variable_names: list[str] = []
    tableau: list[list[str]] | None = None
    inverse_basis: list[list[str]] | None = None
    dual_values: list[str] | None = None
    entering_direction: list[str] | None = None
    ratio_test: list[RatioTestEntryResponse] = []
    pivot: PivotInfoResponse | None = None
    entering_reason: str | None = None
    leaving_reason: str | None = None
    is_degenerate: bool = False


class StandardFormConstraintResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    index: int
    original_equation: str
    standard_equation: str
    flipped: bool
    added_variables: list[str]
    note: str


class StandardFormResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    direction: Literal["max", "min"]
    original_objective: str
    standard_objective: str
    objective_note: str
    variable_names: list[str]
    decision_variables: list[str]
    slack_variables: list[str]
    surplus_variables: list[str]
    artificial_variables: list[str]
    initial_basis: list[str]
    constraints: list[StandardFormConstraintResponse]


class ConstraintResultResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    constraint_index: int
    sense: Literal["<=", ">=", "="]
    lhs_value: str
    rhs_value: str
    slack_or_surplus: str
    type: Literal["holgura", "exceso", "igualdad"]
    variable_name: str | None = None
    is_binding: bool


class SpecialCasesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_infeasible: bool
    is_unbounded: bool
    is_degenerate: bool
    degenerate_during_iterations: bool
    degenerate_variables: list[str]
    has_multiple_optima: bool
    alternative_solutions: list[dict[str, str]]
    messages: list[str]


class ObjectiveRangeResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    variable: str
    optimal_value: str
    is_basic: bool
    reduced_cost: str
    current_coefficient: str
    allowable_decrease: str | None = None
    allowable_increase: str | None = None
    min_value: str | None = None
    max_value: str | None = None
    interpretation: str


class RhsRangeResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    constraint_index: int
    sense: Literal["<=", ">=", "="]
    slack_or_surplus: str
    type: Literal["holgura", "exceso", "igualdad"]
    is_binding: bool
    shadow_price: str
    current_rhs: str
    allowable_decrease: str | None = None
    allowable_increase: str | None = None
    min_value: str | None = None
    max_value: str | None = None
    interpretation: str


class SensitivityResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    applicable: bool
    message: str
    objective_ranges: list[ObjectiveRangeResponse] = []
    rhs_ranges: list[RhsRangeResponse] = []
    notes: list[str] = []


class GraphicalPointResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    x1: str
    x2: str
    x1_float: float
    x2_float: float


class GraphicalVertexResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    x1: str
    x2: str
    x1_float: float
    x2_float: float
    z: str
    z_float: float
    is_optimal: bool


class GraphicalLineResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    index: int | None = None
    label: str
    equation: str
    sense: Literal["<=", ">=", "="] | None = None
    points: list[GraphicalPointResponse]


class GraphicalBoundsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    x_min: float
    x_max: float
    y_min: float
    y_max: float


class GraphicalResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    applicable: bool
    message: str
    region_type: Literal["bounded", "unbounded", "empty", "segment", "point"] | None = None
    bounds: GraphicalBoundsResponse | None = None
    feasible_polygon: list[GraphicalPointResponse] = []
    vertices: list[GraphicalVertexResponse] = []
    constraint_lines: list[GraphicalLineResponse] = []
    objective_line: GraphicalLineResponse | None = None
    optimal_segment: list[GraphicalVertexResponse] = []


class SolveResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["optimal", "infeasible", "unbounded", "iteration_limit"]
    method: Literal["big_m", "revised_simplex"]
    mode: Literal["step_by_step", "direct"] = "step_by_step"
    objective_value: str | None
    solution: dict[str, str] | None
    iterations: list[IterationResponse]
    standard_form: StandardFormResponse
    constraint_results: list[ConstraintResultResponse] = []
    special_cases: SpecialCasesResponse
    sensitivity: SensitivityResponse
    graphical: GraphicalResponse


class ComparisonStepResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    step: int
    big_m_basis: list[str] | None = None
    big_m_entering: str | None = None
    big_m_leaving: str | None = None
    big_m_z: str | None = None
    revised_phase: str | None = None
    revised_basis: list[str] | None = None
    revised_entering: str | None = None
    revised_leaving: str | None = None
    revised_z: str | None = None


class ComparisonSummaryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    big_m_iterations: int
    revised_simplex_iterations: int
    revised_phase1_iterations: int
    revised_phase2_iterations: int
    same_status: bool
    same_objective_value: bool
    same_solution: bool
    summary: str
    steps: list[ComparisonStepResponse]


class CompareResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    big_m: SolveResponse
    revised_simplex: SolveResponse
    comparison: ComparisonSummaryResponse
