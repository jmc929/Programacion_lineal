from fractions import Fraction
from typing import Annotated, Literal, Union

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    StrictInt,
    StrictStr,
    model_validator,
)


def _validate_rational_input(value):
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise ValueError(
            "Los coeficientes deben ser enteros o cadenas racionales; "
            'por ejemplo: 2, "0.25" o "1/4".'
        )
    if isinstance(value, str) and not value.strip():
        raise ValueError("No se permiten campos vacíos en coeficientes o lados derechos.")
    try:
        Fraction(value)
    except ZeroDivisionError:
        raise ValueError("No se permite división por cero en una fracción.") from None
    except ValueError:
        raise ValueError("El valor debe representar un número o fracción válida.") from None
    return value


RationalInput = Annotated[
    Union[StrictInt, StrictStr],
    BeforeValidator(_validate_rational_input),
]


class ConstraintRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    coefficients: list[RationalInput] = Field(min_length=1)
    sense: Literal["<=", ">=", "="]
    rhs: RationalInput


class ProblemRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    objective: list[RationalInput] = Field(min_length=1)
    constraints: list[ConstraintRequest] = Field(default_factory=list)
    direction: Literal["max", "min"] = "max"
    method: Literal["big_m", "revised_simplex"] = "big_m"
    mode: Literal["step_by_step", "direct"] = "step_by_step"
    max_iterations: int = Field(default=1000, strict=True, ge=1, le=10000)

    @model_validator(mode="after")
    def validate_constraint_dimensions(self):
        variable_count = len(self.objective)
        for index, constraint in enumerate(self.constraints, start=1):
            if len(constraint.coefficients) != variable_count:
                raise ValueError(
                    "La restricción {} tiene {} coeficientes; se esperaban {}.".format(
                        index,
                        len(constraint.coefficients),
                        variable_count,
                    )
                )
        return self
