import React, { useState } from 'react';
import { Card } from '../common/Card';

export function IterationsTable({ iterations }) {
  const [selectedIteration, setSelectedIteration] = useState(0);

  if (!iterations || iterations.length === 0) return null;

  const currentIter = iterations[selectedIteration] || iterations[0];

  return (
    <Card title="Evolución de las Iteraciones" className="iterations-card">
      <div className="iteration-tabs">
        {iterations.map((iter, idx) => (
          <button
            key={idx}
            className={`tab-btn ${selectedIteration === idx ? 'active' : ''}`}
            onClick={() => setSelectedIteration(idx)}
          >
            Iteración {iter.iteration} {iter.phase ? `(Fase ${iter.phase})` : ''}
          </button>
        ))}
      </div>

      <div className="iteration-meta-grid">
        <div className="meta-box">
          <div className="meta-box-label">Variables Básicas</div>
          <div className="meta-box-value">{currentIter.basic_variables.join(', ')}</div>
        </div>
        <div className="meta-box">
          <div className="meta-box-label">Valor de Z</div>
          <div className="meta-box-value" style={{ color: 'var(--primary)' }}>
            {currentIter.objective_value}
          </div>
        </div>
        {currentIter.entering_variable && (
          <div className="meta-box">
            <div className="meta-box-label">Variable Entrante</div>
            <div className="meta-box-value" style={{ color: 'var(--success)' }}>
              &darr; {currentIter.entering_variable}
            </div>
          </div>
        )}
        {currentIter.leaving_variable && (
          <div className="meta-box">
            <div className="meta-box-label">Variable Saliente</div>
            <div className="meta-box-value" style={{ color: 'var(--danger)' }}>
              &uarr; {currentIter.leaving_variable}
            </div>
          </div>
        )}
      </div>

      <h4 style={{ marginBottom: '0.75rem', color: 'var(--text-secondary)' }}>
        Valores de la Base:
      </h4>
      <div className="modern-table-wrapper">
        <table className="modern-table">
          <thead>
            <tr>
              <th>Variable Básica</th>
              <th>Valor Racional Exacto</th>
            </tr>
          </thead>
          <tbody>
            {currentIter.basic_variables.map((vName, idx) => (
              <tr key={idx}>
                <td><strong>{vName}</strong></td>
                <td className="mono-cell">{currentIter.basic_values[idx]}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}
