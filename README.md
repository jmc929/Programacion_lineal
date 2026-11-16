# Programación lineal

Implementación en Python de los métodos Big M (tableau) y simplex revisado
(dos fases). Los dos aceptan problemas de maximización o minimización, variables
de decisión no negativas y restricciones `<=`, `>=` o `=`.

## Aritmética exacta

Todos los valores numéricos de entrada se convierten a `fractions.Fraction`.
Para conservar el decimal escrito, los coeficientes pueden pasarse como cadenas
(por ejemplo, `"0.1"`); los `float` se convierten usando su representación
decimal, no mediante la aproximación binaria interna. Big M se maneja
simbólicamente como un par de fracciones `(coeficiente de M, término constante)`.

## Uso

Desde `Backend_programación_lineal`:

```python
from fractions import Fraction
from app.algorithms.big_m import solve_big_m
from app.algorithms.revised_simplex import solve_revised_simplex

objective = [3, 2]
matrix = [[1, 1], [1, 0], [0, 1]]
rhs = [4, 2, 3]
senses = ["<=", "<=", "<="]

result = solve_big_m(objective, matrix, rhs, senses, direction="max")
# También: solve_revised_simplex(objective, matrix, rhs, senses, direction="max")

assert result["status"] == "optimal"
assert result["objective_value"] == Fraction(10)
assert result["solution"] == {"x1": Fraction(2), "x2": Fraction(2)}
```

La firma de ambos métodos es:

```python
solve_...(objective, matrix, rhs, senses, direction="max", max_iterations=1000)
```

`direction` puede ser `"max"` o `"min"`. El resultado contiene `status`
(`"optimal"`, `"infeasible"`, `"unbounded"` o `"iteration_limit"`),
`objective_value`, `solution` y `iterations`. Cuando no hay óptimo finito,
`objective_value` y `solution` son `None`. Cada iteración guarda valores,
costos reducidos y variables entrante/saliente como fracciones exactas; Big M
representa sus costos y su objetivo penalizado con pares de fracciones.

## Pruebas

```powershell
Set-Location Backend_programación_lineal
python -m unittest discover -s tests -v
```

