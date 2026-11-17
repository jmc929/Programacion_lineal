import React from 'react';
import { Card, Button } from '../components/common';

export function HomePage({ onNavigate }) {
  return (
    <div className="page-container home-page">
      <section className="hero-section">
        <h1>📐 Solucionador de Programación Lineal</h1>
        <p className="hero-subtitle">
          Optimización matemática con <strong>aritmética racional exacta</strong>.
          Sin aproximaciones ni errores de punto flotante.
        </p>
        <div className="hero-actions">
          <Button variant="primary" onClick={() => onNavigate('solver')}>
            Comenzar a Resolver
          </Button>
          <Button variant="secondary" onClick={() => onNavigate('about')}>
            Conocer los Métodos
          </Button>
        </div>
      </section>

      <section className="features-grid">
        <Card title="Aritmética Exacta">
          <p>
            Todos los coeficientes y cálculos se gestionan como fracciones puras
            (<code>fractions.Fraction</code>). Garantiza resultados exactos sin
            redondeos acumulados.
          </p>
        </Card>

        <Card title="Método de la Gran M">
          <p>
            Resolución mediante <em>Tableau</em> simplex con variables artificiales.
            La penalización <em>M</em> se manipula simbólicamente como un par exacto{' '}
            <code>(coeficiente M, constante)</code>.
          </p>
        </Card>

        <Card title="Simplex Revisado">
          <p>
            Implementación en dos fases utilizando álgebra de matrices exacta,
            inversión de base (<em>B<sup>-1</sup></em>) y cálculo de costos reducidos.
          </p>
        </Card>
      </section>

      <Card title="¿Cómo empezar?" className="getting-started-card">
        <ol className="steps-list">
          <li>
            Haz clic en <strong>Comenzar a Resolver</strong>.
          </li>
          <li>Selecciona la cantidad de variables de decisión y el método deseado.</li>
          <li>
            Introduce los coeficientes de la función objetivo y las restricciones (puedes
            usar enteros como <code>3</code> o fracciones como <code>1/2</code> o <code>0.25</code>).
          </li>
          <li>
            Presiona <strong>Resolver Problema</strong> para ver la solución óptima y
            cada una de las iteraciones paso a paso.
          </li>
        </ol>
      </Card>
    </div>
  );
}
