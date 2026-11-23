# Manual de Usuario — Aplicación de Programación Lineal

**Universidad de Antioquia — Facultad de Ingeniería — Departamento de Ingeniería de Sistemas**  
**Asignatura:** Optimización (Investigación de Operaciones I)

---

## 1. Introducción y Acceso

Esta aplicación web permite formular, resolver y analizar problemas de programación lineal ($x_i \ge 0$) utilizando implementaciones propias del **Método de la Gran M** y del **Método Simplex Revisado (Dos Fases)** con aritmética racional exacta (fracciones sin errores de redondeo).

### Cómo iniciar la aplicación
1. **Con Docker:** Ejecute `docker compose up --build` en la raíz del repositorio y abra `http://localhost:8000` en su navegador.
2. **En modo desarrollo:** Inicie el backend (`uvicorn app.main:app --reload`) y el frontend (`npm run dev`), luego abra `http://localhost:5173`.
3. En la pantalla de inicio, haga clic en **Abrir Solucionador**.

---

## 2. Guía de la Interfaz

### 2.1 Barra de Ejemplos y Archivos (JSON / CSV)
En la parte superior del solucionador encontrará:
- **Ejemplos de evaluación:** menú desplegable con los 7 casos tipo del curso precargados.
- **Cargar JSON / CSV:** importa un problema previamente guardado desde su equipo.
- **Guardar JSON / Guardar CSV:** descarga el modelo actual para reutilizarlo después.

### 2.2 Configuración del Modelo
1. **Cantidad de Variables de Decisión:** escriba el número de variables ($1$ a $50$) o utilice los botones `−` y `+ xN`.
2. **Método Algorítmico:** elija entre:
   - *Método de la Gran M (Tableau Simplex)*
   - *Simplex Revisado (Dos Fases Matricial)*
   - *Comparar Ambos (Gran M vs. Simplex Revisado)*
3. **Modo de Solución:** elija entre **Paso a paso** (muestra la forma estándar y cada iteración) o **Solución directa** (muestra únicamente el resultado final).
4. **Función Objetivo:** seleccione **Maximizar (Z)** o **Minimizar (Z)** e ingrese coeficientes enteros (`50`), decimales (`0.25`) o fracciones (`3/4`).
5. **Restricciones:** agregue restricciones con `+ Nueva Restricción`, seleccione el sentido (`≤`, `≥`, `=`) e ingrese el lado derecho (RHS), que puede ser positivo, cero o negativo.
6. Haga clic en **⚡ Resolver Modelo**. Si algún campo está vacío, tiene texto no numérico o división por cero, el formulario resalta el campo y muestra un mensaje claro de corrección.

### 2.3 Secciones de Resultados
Una vez resuelto el modelo (sin necesidad de reiniciar para editar y volver a resolver), los resultados se presentan en secciones claras:
- **Resumen del Modelo:** estado (Óptimo, Infactible, No acotado), avisos de casos especiales (soluciones óptimas múltiples o degeneración), valor óptimo $Z^*$, valores de $x_i$ y tabla de **holgura o exceso** de cada restricción.
- **Paso a Paso:** forma estándar del modelo + iteraciones navegables (por pestañas o todas a la vez) con tablero completo o matriz $B^{-1}$, costos reducidos, prueba de la razón mínima, elemento pivote resaltado y justificación de entrada/salida.
- **Método Gráfico:** gráfica interactiva en el primer cuadrante para $n=2$ (región factible, restricciones rotuladas, vértices con su $Z$ y recta de isoutilidad). Para $n \neq 2$ muestra un aviso claro de que no aplica.
- **Análisis de Sensibilidad:** tablas de rangos de $c_j$, costos reducidos, precios sombra, rangos de $b_i$ e interpretación en texto.
- **Comparación de Métodos:** compara iteración por iteración Gran M frente a Simplex Revisado.
- **Exportar Paso a Paso a PDF:** descarga un reporte PDF completo con todo el procedimiento y la gráfica vectorial.

---

## 3. Problema Resuelto 1: Maximización, Restricción Redundante y Método Gráfico

**Formulación:**
$$\max Z = 50x_1 + 80x_2$$
sujeto a:
- $R_1: 2x_1 + x_2 \le 100$
- $R_2: x_1 + 3x_2 \le 90$
- $R_3: x_2 \le 40$
- $x_1, x_2 \ge 0$

**Pasos en la aplicación:**
1. Seleccione *Ej. 1 — Estándar, redundante y gráfico* (o ingrese los datos manualmente).
2. Seleccione **Método de la Gran M** y modo **Paso a paso**, luego pulse **Resolver Modelo**.

**Resultados obtenidos:**
- **Forma estándar:** se añaden holguras $s_1, s_2, s_3$ con base inicial $\{s_1, s_2, s_3\}$.
- **Iteraciones (3 tablas):**
  - Iteración 0: entra $x_1$ ($C_j - Z_j = 50$), sale $s_1$ (razón mínima $100/2 = 50$, pivote $2$).
  - Iteración 1: entra $x_2$ ($C_j - Z_j = 55$), sale $s_2$ (razón mínima $40 / (5/2) = 16$, pivote $5/2$).
  - Iteración 2 (Óptimo): todos los $C_j - Z_j \le 0$.
- **Solución óptima:** $x_1 = 42$, $x_2 = 16$, $Z^* = 3380$.
- **Holguras:** $R_1 = 0$ (activa), $R_2 = 0$ (activa), $R_3 = 24$ (no activa / redundante).
- **Método gráfico:** muestra los 4 vértices $(0,0)$, $(50,0)$, $(42,16)^*$ y $(0,30)$ con la recta óptima $50x_1 + 80x_2 = 3380$.
- **Sensibilidad:**
  - $c_1 \in [80/3,\, 160]$, $c_2 \in [25,\, 150]$.
  - Precios sombra: $R_1 = 14$ ($b_1 \in [30, 180]$), $R_2 = 22$ ($b_2 \in [50, 150]$), $R_3 = 0$ ($b_3 \in [16, +\infty)$).

> *[Espacio para captura de pantalla 1: Vista de Solución, Tablero Paso a Paso y Método Gráfico del Problema 1]*

---

## 4. Problema Resuelto 2: Minimización con `=`, `≥` y Lado Derecho Negativo

**Formulación:**
$$\min Z = 4x_1 + x_2$$
sujeto a:
- $R_1: 3x_1 + x_2 = 3$
- $R_2: 4x_1 + 3x_2 \ge 6$
- $R_3: -x_1 - 2x_2 \ge -4$
- $x_1, x_2 \ge 0$

**Pasos en la aplicación:**
1. Seleccione *Ej. 2 — Minimización, =, ≥, RHS negativo* y elija **Comparar Ambos (Gran M vs. Simplex Revisado)**.
2. Pulse **Resolver y Comparar Ambos Métodos**.

**Resultados obtenidos:**
- **Forma estándar:**
  - El objetivo se transforma a $\max Z' = -4x_1 - x_2$.
  - $R_3$ tiene RHS negativo ($-4$): se multiplica por $-1$ quedando $x_1 + 2x_2 \le 4$ y se añade holgura $+s_3$.
  - $R_1$ añade artificial $+a_1$; $R_2$ resta exceso $-e_2$ y añade artificial $+a_2$.
- **Solución óptima (exacta en fracciones):** $x_1 = 2/5$, $x_2 = 9/5$, $Z^* = 17/5$.
- **Holguras y excesos:** $R_1 = 0$ (igualdad), $R_2 = 1$ (exceso $e_2 = 1$, no activa), $R_3 = 0$ (holgura $s_3 = 0$, activa).
- **Método gráfico:** identifica que la región factible es el segmento de recta entre $(2/5, 9/5)$ ($Z = 17/5$, óptimo) y $(3/5, 6/5)$ ($Z = 18/5$).
- **Sensibilidad:** precios sombra $R_1 = 7/5$, $R_2 = 0$, $R_3 = 1/5$ con rangos $b_1 \in [2, 12]$, $b_2 \in (-\infty, 7]$ y $b_3 \in [-6, -3]$.
- **Comparación:** Gran M converge en 4 iteraciones y Simplex Revisado en 5 iteraciones (Fase I + Fase II), ambos con resultado idéntico.

> *[Espacio para captura de pantalla 2: Vista de Comparación Gran M vs. Simplex Revisado y Análisis de Sensibilidad del Problema 2]*

---

## 5. Formato de Archivos JSON y CSV Soportados

### Ejemplo JSON
```json
{
  "direction": "max",
  "method": "big_m",
  "objective": ["50", "80"],
  "constraints": [
    { "coefficients": ["2", "1"], "sense": "<=", "rhs": "100" },
    { "coefficients": ["1", "3"], "sense": "<=", "rhs": "90" }
  ]
}
```

### Ejemplo CSV
```csv
type,x1,x2,sense,rhs
max,50,80,,
R1,2,1,<=,100
R2,1,3,<=,90
```
