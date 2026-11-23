import React from 'react';
import { Card } from '../components/common';

export function AboutPage() {
  return (
    <div className="page-container about-page">
      <div className="page-header">
        <h2>Fundamentos y Métodos de Solución</h2>
        <p>Conoce los pilares matemáticos y algorítmicos implementados desde cero en esta aplicación.</p>
      </div>

      <Card title="Aritmética Racional Exacta">
        <p style={{ color: 'var(--text-secondary)', lineHeight: '1.7' }}>
          Todas las operaciones algebraicas (pivoteos, inversión de matrices, razones mínimas,
          intersecciones geométricas y rangos de sensibilidad) se realizan mediante <code>fractions.Fraction</code>,
          eliminando los errores de redondeo de punto flotante IEEE 754.
        </p>
      </Card>

      <Card title="Método de la Gran M (Tableau Simplex)">
        <p style={{ color: 'var(--text-secondary)', lineHeight: '1.7' }}>
          Normaliza las restricciones agregando variables de holgura (<code>+s</code>), exceso (<code>-e</code>)
          y artificiales (<code>+a</code>). En lugar de sustituir <em>M</em> por un número grande arbitrario,
          cada costo reducido se calcula simbólicamente como un par exacto <code>(coeficiente_M, constante)</code>
          y se aplica la regla de Bland para evitar ciclos en casos degenerados.
        </p>
      </Card>

      <Card title="Método Simplex Revisado (Dos Fases)">
        <p style={{ color: 'var(--text-secondary)', lineHeight: '1.7' }}>
          Mantiene la matriz inversa de la base <em>B<sup>-1</sup></em> mediante eliminación de Gauss-Jordan exacta.
          Calcula los multiplicadores simplex <code>yᵀ = c_Bᵀ B⁻¹</code>, los costos reducidos y el vector dirección
          <code>d = B⁻¹ a_j</code>. Cuando existen variables artificiales, ejecuta la Fase I para obtener una base
          inicial factible antes de optimizar el objetivo original en la Fase II.
        </p>
      </Card>

      <Card title="Método Gráfico y Análisis de Sensibilidad">
        <p style={{ color: 'var(--text-secondary)', lineHeight: '1.7' }}>
          Para modelos de 2 variables, las intersecciones de rectas y el recorte de la región factible se calculan
          con geometría racional exacta (Sutherland-Hodgman), distinguiendo regiones acotadas, no acotadas,
          vacías y segmentos por igualdad. A partir de la base óptima <em>B<sup>-1</sup></em> se obtienen los
          precios sombra, costos reducidos, rangos de optimalidad para <code>cⱼ</code> y rangos de factibilidad para <code>bᵢ</code>.
        </p>
      </Card>
    </div>
  );
}
