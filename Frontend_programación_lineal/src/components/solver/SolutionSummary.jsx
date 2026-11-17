import React from 'react';
import { Card } from '../common/Card';

export function SolutionSummary({ result }) {
  if (!result) return null;

  const { status, objective_value, solution } = result;

  const statusLabels = {
    optimal: { text: 'Solución Óptima Encontrada', class: 'status-optimal' },
    infeasible: { text: 'Problema Infactible (Sin solución)', class: 'status-infeasible' },
    unbounded: { text: 'Problema No Acotado (Z ilimitado)', class: 'status-unbounded' },
    iteration_limit: { text: 'Límite de Iteraciones Alcanzado', class: 'status-limit' },
  };

  const currentStatus = statusLabels[status] || { text: status, class: '' };

  return (
    <Card title="Resultado Final" className="solution-summary-card">
      <div className={`status-badge ${currentStatus.class}`}>
        {currentStatus.text}
      </div>

      {status === 'optimal' && (
        <div className="solution-details">
          <div className="optimal-value">
            <strong>Valor Óptimo (Z*): </strong>
            <span className="fraction-highlight">{objective_value}</span>
          </div>

          <div className="variables-list">
            <h4>Valores de las Variables:</h4>
            <ul>
              {solution &&
                Object.entries(solution).map(([variable, val]) => (
                  <li key={variable}>
                    <strong>{variable}</strong> = {val}
                  </li>
                ))}
            </ul>
          </div>
        </div>
      )}
    </Card>
  );
}
