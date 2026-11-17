import React from 'react';
import { Card } from '../components/common';

export function AboutPage() {
  return (
    <div className="page-container about-page">
      <div className="page-header">
        <h2>Fundamentos y Métodos de Solución</h2>
        <p>Conoce los pilares matemáticos y algorítmicos detrás de este optimizador.</p>
      </div>

      <Card title="Aritmética Racional Exacta">
        <p style={{ color: 'var(--text-secondary)', lineHeight: '1.7' }}>
          La mayoría de herramientas científicas convierten los números a representación binaria de punto flotante
          (IEEE 754), acumulando errores de redondeo que pueden conducir a errores en el pivoteo o falsas conclusiones
          sobre la factibilidad.
        </p>
        <p style={{ color: 'var(--text-secondary)', marginTop: '0.75rem', lineHeight: '1.7' }}>
          Este motor procesa y simplifica cada número como una fracción exacta mediante <code>fractions.Fraction</code> de Python,
          garantizando respuestas matemáticas 100% fieles a la teoría lineal.
        </p>
      </Card>

      <Card title="Método de la Gran M (Tableau Simplex)">
        <p style={{ color: 'var(--text-secondary)', lineHeight: '1.7' }}>
          Permite resolver problemas con restricciones de tipo <code>&ge;</code> o <code>=</code> agregando variables
          artificiales con un coste penalizado <em>M</em> extremadamente grande.
        </p>
        <p style={{ color: 'var(--text-secondary)', marginTop: '0.75rem', lineHeight: '1.7' }}>
          En lugar de sustituir <em>M</em> por un número arbitrario (como <code>1000000</code>, lo cual causa inestabilidad numérica),
          cada coste reducido y valor objetivo se almacena algebraicamente como un par <code>(coeficiente_M, constante)</code>.
        </p>
      </Card>

      <Card title="Método Simplex Revisado">
        <p style={{ color: 'var(--text-secondary)', lineHeight: '1.7' }}>
          Es computacionalmente más eficiente para problemas de gran escala. En cada iteración mantiene y actualiza únicamente
          la inversa de la base <em>B<sup>-1</sup></em>, calculando los costes reducidos y la dirección de avance sin necesidad de
          transformar la matriz de restricciones completa en cada paso.
        </p>
      </Card>
    </div>
  );
}
