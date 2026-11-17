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

## Ejecución rápida con Docker (Frontend + Backend en un solo contenedor)

Para levantar la aplicación completa (interfaz web en React + backend en FastAPI) con un solo comando:

```bash
docker compose up --build
```

O utilizando directamente la imagen Docker:

```bash
docker build -t linear-solver .
docker run -p 8000:8000 linear-solver
```

Una vez iniciado el contenedor:
- **Interfaz Web (Frontend React):** `http://localhost:8000`
- **Documentación Interactiva Swagger (API):** `http://localhost:8000/docs`
- **Endpoint de salud:** `http://localhost:8000/api/health`


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
Set-Location "Backend_programación_lineal"
py -3 -m unittest discover -s tests -v
```

## API HTTP

La API está construida con FastAPI. Desde la raíz del proyecto, instala las
dependencias y arranca el servidor de desarrollo:

```powershell
Set-Location "Backend_programación_lineal"
py -3 -m pip install -r requirements.txt
py -3 -m uvicorn app.main:app --reload
```

La documentación interactiva se encuentra en `http://127.0.0.1:8000/docs`.
`GET /api/health` comprueba el estado del servicio y `POST /api/solve` resuelve
un problema. Ejemplo de cuerpo JSON:

```json
{
  "objective": ["3", "2"],
  "constraints": [
    {"coefficients": ["1", "1"], "sense": "<=", "rhs": "4"},
    {"coefficients": ["1", "0"], "sense": "<=", "rhs": "2"},
    {"coefficients": ["0", "1"], "sense": "<=", "rhs": "3"}
  ],
  "direction": "max",
  "method": "big_m",
  "max_iterations": 1000
}
```

`objective` y cada restricción deben tener dimensiones consistentes. Los
coeficientes aceptan enteros JSON o cadenas racionales (`"0.1"`, `"1/3"`);
los números JSON decimales se rechazan para evitar conversiones implícitas a
binario. Las fracciones se devuelven como cadenas exactas, por ejemplo `"3/10"`.
`method` puede ser `"big_m"` o `"revised_simplex"`.

