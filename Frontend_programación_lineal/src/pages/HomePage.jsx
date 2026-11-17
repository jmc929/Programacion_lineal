import React from 'react';
import { Card, Button } from '../components/common';

export function HomePage({ onNavigate }) {
  return (
    <div className="page-container home-page">
      <section className="hero-section">
        <div className="hero-badge">
          <span>✨ Precisión Matemática Exacta</span>
        </div>
        <h1>
          Optimización Lineal con <br />
          <span className="gradient-text">Aritmética Racional Pura</span>
        </h1>
        <p className="hero-subtitle">
          Resuelve modelos de programación lineal paso a paso sin tolerar errores
          de redondeo decimal. Soporta <strong>Big M (Tableau)</strong> y <strong>Simplex Revisado en dos fases</strong>.
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
          <h3>Cero Errores de Redondeo</h3>
          <p>
            Cada operación se realiza mediante fracciones matemáticas irreducibles
            (<code>fractions.Fraction</code>), preservando los valores exactos como <code>1/3</code> o <code>0.1</code>.
          </p>
        </div>

        <div className="feature-card">
          <div className="feature-icon-wrapper">⚡</div>
          <h3>Método de la Gran M</h3>
          <p>
            Tratamiento formal y simbólico de <em>M</em> con pares de costos
            <code>(coeficiente_M, constante)</code>. Visualiza pivoteos e iteraciones del tableau completo.
          </p>
        </div>

        <div className="feature-card">
          <div className="feature-icon-wrapper">📊</div>
          <h3>Simplex Revisado</h3>
          <p>
            Inversión explícita de la base <em>B<sup>-1</sup></em>, cálculo de multiplicadores simplex
            y resolución bifásica para problemas con restricciones <code>&ge;</code> o <code>=</code>.
          </p>
        </div>
      </div>

      <Card title="Guía Rápida">
        <ol className="steps-list">
          <li>
            Haz clic en <strong>Abrir Solucionador</strong> para comenzar.
          </li>
          <li>Indica el número de variables y elige entre maximizar o minimizar.</li>
          <li>
            Ingresa los coeficientes como enteros (<code>4</code>) o fracciones (<code>3/4</code>, <code>0.25</code>).
          </li>
          <li>
            Ejecuta el cálculo para inspeccionar tanto la <strong>solución óptima</strong> como las <strong>tablas de cada iteración</strong>.
          </li>
        </ol>
      </Card>
    </div>
  );
}
