import React from 'react';
import { Card, Button } from '../components/common';

export function HomePage({ onNavigate }) {
  return (
    <div className="page-container home-page">
      <section className="hero-section">
        <div className="hero-badge">
          <span>✨ Optimización — Programación Lineal Exacta</span>
        </div>
        <h1>
          Optimización Lineal con <br />
          <span className="gradient-text">Aritmética Racional Pura</span>
        </h1>
        <p className="hero-subtitle">
          Resuelve modelos de programación lineal paso a paso sin errores de redondeo.
          Incluye <strong>Gran M</strong>, <strong>Simplex Revisado</strong>,{' '}
          <strong>Método Gráfico 2D</strong>, <strong>Análisis de Sensibilidad</strong> y exportación a PDF.
        </p>
        <div className="hero-actions">
          <Button variant="primary" onClick={() => onNavigate('solver')}>
            Abrir Solucionador &rarr;
          </Button>
          <Button variant="secondary" onClick={() => onNavigate('about')}>
            Ver Teoría y Métodos
          </Button>
        </div>
      </section>

      <div className="features-grid">
        <div className="feature-card">
          <div className="feature-icon-wrapper">🎯</div>
          <h3>Fracciones Exactas</h3>
          <p>
            Cada operación se calcula con fracciones irreducibles (<code>fractions.Fraction</code>),
            preservando valores como <code>17/5</code> o <code>1/3</code> en todo el paso a paso.
          </p>
        </div>

        <div className="feature-card">
          <div className="feature-icon-wrapper">⚡</div>
          <h3>Gran M y Simplex Revisado</h3>
          <p>
            Resuelve y compara ambos algoritmos propios: tablero completo con <em>M</em> simbólico o
            inversa de la base <em>B<sup>-1</sup></em> en dos fases, con prueba de razón mínima y justificación.
          </p>
        </div>

        <div className="feature-card">
          <div className="feature-icon-wrapper">📐</div>
          <h3>Método Gráfico 2D</h3>
          <p>
            Para problemas de 2 variables grafica región factible, restricciones rotuladas,
            vértices con su <em>Z</em> y recta de isoutilidad, incluso para casos no acotados o infactibles.
          </p>
        </div>

        <div className="feature-card">
          <div className="feature-icon-wrapper">📊</div>
          <h3>Análisis de Sensibilidad</h3>
          <p>
            Calcula precios sombra, costos reducidos, rangos de coeficientes de la función objetivo
            y rangos de lados derechos con interpretación clara.
          </p>
        </div>

        <div className="feature-card">
          <div className="feature-icon-wrapper">🔍</div>
          <h3>Casos Especiales</h3>
          <p>
            Detecta e informa de forma explícita problemas infactibles, no acotados,
            soluciones óptimas múltiples (con vértices alternativos) y soluciones degeneradas.
          </p>
        </div>

        <div className="feature-card">
          <div className="feature-icon-wrapper">📥</div>
          <h3>Exportación PDF y JSON/CSV</h3>
          <p>
            Guarda y carga modelos en JSON o CSV, y exporta el reporte completo del proceso paso a paso,
            gráfico y sensibilidad directamente a PDF.
          </p>
        </div>
      </div>

      <Card title="Guía Rápida">
        <ol className="steps-list">
          <li>
            Haz clic en <strong>Abrir Solucionador</strong> o carga alguno de los <strong>7 ejemplos de evaluación</strong>.
          </li>
          <li>
            Define variables, criterio (<strong>Max/Min</strong>), restricciones (<code>≤</code>, <code>≥</code>, <code>=</code> con lados derechos de cualquier signo), método y modo (<strong>Directo</strong> o <strong>Paso a paso</strong>).
          </li>
          <li>
            Ejecuta el cálculo para explorar el <strong>resumen con holguras/excesos</strong>, el <strong>paso a paso completo</strong>, el <strong>método gráfico</strong> y el <strong>análisis de sensibilidad</strong>.
          </li>
        </ol>
      </Card>
    </div>
  );
}
