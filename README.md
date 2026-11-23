# Aplicación de Programación Lineal — Optimización

Aplicación web con interfaz gráfica interactiva para formular, resolver y analizar problemas de programación lineal mediante **implementaciones propias** de los métodos de la **Gran M (Tableau)** y **Simplex Revisado (Dos Fases)**, operando en **aritmética racional exacta** (`fractions.Fraction`) sin librerías externas de optimización.

---

## Funcionalidades Implementadas

### Requisitos obligatorios
- **Entrada y validación completa:** Soporta maximización o minimización (`max` / `min`), $n$ variables de decisión no negativas ($x_i \ge 0$), $m$ restricciones (`<=`, `>=`, `=`) y lados derechos de cualquier signo (incluidos negativos). Valida campos vacíos, división por cero, valores no numéricos, variables duplicadas y dimensiones inconsistentes con mensajes claros.
- **Métodos propios en fracciones exactas:**
  - **Método de la Gran M:** manejo simbólico de $M$ como pares exactos `(coef_M, constante)` y regla de Bland para evitar ciclos.
  - **Simplex Revisado (Dos Fases):** cálculo explícito de $B^{-1}$ mediante eliminación de Gauss-Jordan racional, multiplicadores simplex $y^T = c_B^T B^{-1}$, costos reducidos y vector dirección $d = B^{-1}a_j$.
- **Dos modos de solución:** **Solución directa** (solo resultado final) o **Paso a paso** (forma estándar con holguras `s`, excesos `e` y artificiales `a`, tablero completo o matriz $B^{-1}$, costos reducidos, prueba de la razón mínima, elemento pivote y justificación de cada decisión).
- **Solución óptima completa:** valor óptimo $Z^*$, valor de cada variable de decisión y **holgura o exceso** de cada restricción.
- **Método gráfico (2 variables):** región factible sombreada, restricciones rotuladas, vértices con coordenadas exactas y valor de $Z$, recta de isoutilidad/isocosto en el óptimo, segmento óptimo en soluciones múltiples, y soporte para regiones no acotadas, vacías (infactibles) o unidimensionales (igualdades). Si $n \neq 2$, indica claramente que el método gráfico no aplica.
- **Análisis de sensibilidad:** precios sombra, costos reducidos, rangos de optimalidad para cada $c_j$, rangos de factibilidad para cada $b_i$ e interpretación en lenguaje natural.
- **Detección de casos especiales:** informa con mensajes claros problemas **infactibles**, **no acotados**, con **soluciones óptimas múltiples** (incluyendo vértices alternativos) y **degenerados**.

### Bonificaciones implementadas
- **Comparación de ambos métodos (Gran M vs. Simplex Revisado):** vista dedicada y endpoint `/api/compare` comparando iteración por iteración ambos algoritmos.
- **Fracciones exactas en todo el paso a paso:** todos los cálculos y tablas trabajan con números racionales exactos (con opción visual de mostrar equivalencia decimal).
- **Exportación del paso a paso a PDF:** generador PDF nativo en Python (`POST /api/export/pdf`) que descarga un reporte completo con forma estándar, todas las iteraciones, gráfico vectorial 2D y sensibilidad.
- **Cargar y guardar problemas (JSON y CSV):** importación/exportación directa desde la interfaz, además de los 7 problemas de evaluación precargados.

---

## Requisitos del Sistema

- **Opción recomendada (Docker):** Docker Desktop / Docker Engine + Docker Compose.
- **Ejecución local manual:**
  - Python `3.11+`
  - Node.js `20+` y `npm`

---

## Instalación y Ejecución

### Opción 1: Ejecución rápida con Docker (Recomendada)

Levanta el frontend compilado (React + Vite) y el backend (FastAPI) en un solo contenedor:

```bash
docker compose up --build
```

Una vez iniciado:
- **Aplicación Web:** `http://localhost:8000`
- **Documentación Swagger API:** `http://localhost:8000/docs`
- **Estado del servicio:** `http://localhost:8000/api/health`

### Opción 2: Ejecución local en desarrollo

#### 1. Backend (FastAPI)

```powershell
Set-Location "Backend_programación_lineal"
py -3 -m pip install -r requirements.txt
py -3 -m uvicorn app.main:app --reload --port 8000
```

#### 2. Frontend (React + Vite)

En otra terminal:

```powershell
Set-Location "Frontend_programación_lineal"
npm install
npm run dev
```

Abre `http://localhost:5173` en el navegador (Vite redirige automáticamente `/api` al backend en `http://127.0.0.1:8000`).

---

## Pruebas Automatizadas

Desde `Backend_programación_lineal`:

```powershell
py -3 -m unittest discover -s tests -v
```

Las pruebas verifican los **7 problemas de evaluación** del proyecto (estándar/redundante, minimización con `=`, `>=` y RHS negativo, 3 variables, infactible, no acotado, óptimos múltiples y degeneración), la sensibilidad exacta, el método gráfico, los endpoints HTTP (`/api/solve`, `/api/compare`, `/api/export/pdf`) y la generación de PDF.

---

## Endpoints de la API

| Método | Ruta | Descripción |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Comprueba el estado del backend |
| `POST` | `/api/solve` | Resuelve el problema (`method`: `big_m` o `revised_simplex`; `mode`: `step_by_step` o `direct`) |
| `POST` | `/api/compare` | Ejecuta Gran M y Simplex Revisado y compara sus iteraciones |
| `POST` | `/api/export/pdf` | Genera y descarga el reporte paso a paso en formato PDF |

Ejemplo de cuerpo JSON para `POST /api/solve`:

```json
{
  "objective": ["50", "80"],
  "constraints": [
    {"coefficients": ["2", "1"], "sense": "<=", "rhs": "100"},
    {"coefficients": ["1", "3"], "sense": "<=", "rhs": "90"},
    {"coefficients": ["0", "1"], "sense": "<=", "rhs": "40"}
  ],
  "direction": "max",
  "method": "big_m",
  "mode": "step_by_step",
  "max_iterations": 1000
}
```

---

## Documentación Adicional

- **Manual de Usuario:** [docs/Manual_de_Usuario.md](docs/Manual_de_Usuario.md)
