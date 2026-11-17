import React, { useState } from 'react';
import { Card } from '../common/Card';

export function IterationsTable({ iterations, method }) {
  const [selectedIteration, setSelectedIteration] = useState(0);

  if (!iterations || iterations.length === 0) return null;

  const currentIter = iterations[selectedIteration] || iterations[0];

  return (
    <Card title="Iteraciones y Desarrollo Paso a Paso" className="iterations-card">
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

      <div className="iteration-details">
        <div className="iteration-meta">
          <p>
            <strong>Variables Básicas:</strong> {currentIter.basic_variables.join(', ')}
          </p>
          <p>
            <strong>Valor de Z en esta iteración:</strong> {currentIter.objective_value}
          </p>
          {currentIter.entering_variable && (
            <p>
              <strong>Variable Entrante:</strong> {currentIter.entering_variable}
            </p>
          )}
          {currentIter.leaving_variable && (
            <p>
              <strong>Variable Saliente:</strong> {currentIter.leaving_variable}
            </p>
          )}
        </div>

        <h4>Valores Básicos:</h4>
        <div className="basic-values-table">
          <table>
            <thead>
              <tr>
                <th>Variable Básica</th>
                <th>Valor Exacto</th>
              </tr>
            </thead>
            <tbody>
              {currentIter.basic_variables.map((vName, idx) => (
                <tr key={idx}>
                  <td>{vName}</td>
                  <td>{currentIter.basic_values[idx]}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </Card>
  );
}
