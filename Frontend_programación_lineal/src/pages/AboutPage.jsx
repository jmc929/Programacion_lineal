import React from 'react';
import { Card } from '../components/common';

export function AboutPage() {
  return (
    <div className="page-container about-page">
      <h2>Acerca de los Métodos</h2>

      <Card title="Aritmética Exacta con Fracciones">
        <p>
          Este sistema resuelve modelos de programación lineal utilizando aritmética racional
          exacta. Las entradas numéricas y operaciones se representan como fracciones exactas,
          eliminando las imprecisiones de los decimales de punto flotante en la computadora.
        </p>
      </Card>

      <Card title="Método de la Gran M (Big M)">
        <p>
          Agrega variables artificiales con una penalización muy alta (representada simbólicamente
          por <em>M</em>) en la función objetivo. La constante <em>M</em> se manipula formalmente
          como un par <code>(coeficiente_M, constante)</code> sin asignarle un valor numérico arbitrario.
        </p>
      </Card>

      <Card title="Método Simplex Revisado">
        <p>
          Trabaja calculando de forma explícita la inversa de la matriz base <em>B<sup>-1</sup></em> y
          utiliza un enfoque de dos fases cuando se requieren variables artificiales para encontrar una
          solución inicial básica factible.
        </p>
      </Card>
    </div>
  );
}
