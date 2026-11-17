import React from 'react';
import { Card } from '../common/Card';

export function SolutionSummary({ result }) {
  if (!result) return null;

  const { status, objective_value, solution } = result;

  const statusConfig = {
    optimal: { text: '✓ Solución Óptima Encontrada', class: 'status-optimal' },
    infeasible: { text: '✗ Problema Infactible (Sin Solución)', class: 'status-infeasible' },
    unbounded: { text: '⚠ Problema No Acotado (Z Ilimitado)', class: 'status-unbounded' },
    iteration_limit: { text: '⏱ Límite de Iteraciones Alcanzado', class: 'status-limit' },
  };

  const currentStatus = statusConfig[status] || { text: status, class: '' };

  return (
    <Card title="Resultado del Modelo" className="solution-summary-card">
      <div className={`status-badge ${currentStatus.class}`}>
        {currentStatus.text}
      </div>

      {status === 'optimal' && (
        <div className="solution-details">
          <div className="optimal-value-banner">
            <div>
              <div className="optimal-value-label">Valor Óptimo de la Función Objetivo (Z*)</div>
              <div className="fraction-highlight">{objective_value}</div>
            </div>
          </div>

          <h4 style={{ marginBottom: '0.85rem', color: 'var(--text-secondary)' }}>
            Valores Óptimos de las Variables de Decisión:
          </h4>
          <div className="variables-grid">
            {solution &&
              Object.entries(solution).map(([variable, val]) => (
                <div key={variable} className="variable-card">
                  <div className="variable-name">{variable}</div>
                  <div className="variable-val">{val}</div>
                </div>
              ))}
          </div>
        </div>
      )}
    </Card>
  );
}
