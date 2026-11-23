import React from 'react';
import { Card } from '../common/Card';
import { formatFraction } from '../../utils/formatters';

export function SolutionSummary({ result, showDecimal = false }) {
  if (!result) return null;

  const {
    status,
    objective_value,
    solution,
    constraint_results = [],
    special_cases,
    method,
  } = result;

  const statusConfig = {
    optimal: { text: '✓ Solución Óptima Encontrada', class: 'status-optimal' },
    infeasible: { text: '✗ Problema Infactible (Sin Solución Factible)', class: 'status-infeasible' },
    unbounded: { text: '⚠ Problema No Acotado (Z Ilimitado)', class: 'status-unbounded' },
    iteration_limit: { text: '⏱ Límite de Iteraciones Alcanzado', class: 'status-unbounded' },
  };

  const currentStatus = statusConfig[status] || { text: status, class: '' };
  const methodLabel =
    method === 'revised_simplex'
      ? 'Simplex Revisado (Dos Fases)'
      : 'Método de la Gran M (Tableau)';

  return (
    <Card
      title="Resultado del Modelo"
      subtitle={`Resuelto mediante ${methodLabel} con aritmética racional exacta`}
      className="solution-summary-card"
    >
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.6rem', alignItems: 'center', marginBottom: '1rem' }}>
        <div className={`status-badge ${currentStatus.class}`} style={{ marginBottom: 0 }}>
          {currentStatus.text}
        </div>

        {special_cases?.has_multiple_optima && (
          <div className="status-badge status-info" style={{ marginBottom: 0 }}>
            ∞ Soluciones Óptimas Múltiples
          </div>
        )}

        {special_cases?.is_degenerate && (
          <div className="status-badge status-unbounded" style={{ marginBottom: 0 }}>
            ⚡ Solución Degenerada
          </div>
        )}
      </div>

      {/* Mensajes claros de casos especiales (infactible, no acotado, múltiples óptimos, degenerado) */}
      {special_cases?.messages && special_cases.messages.length > 0 && (
        <div
          className={`special-notice-box ${
            status === 'infeasible'
              ? 'special-notice-danger'
              : status === 'unbounded'
              ? 'special-notice-warn'
              : 'special-notice-info'
          }`}
        >
          {special_cases.messages.map((msg, idx) => (
            <p key={idx}>{msg}</p>
          ))}
        </div>
      )}

      {status === 'optimal' && (
        <div className="solution-details">
          <div className="optimal-value-banner">
            <div>
              <div className="optimal-value-label">Valor Óptimo de la Función Objetivo (Z*)</div>
              <div className="fraction-highlight">
                {formatFraction(objective_value, showDecimal)}
              </div>
            </div>
          </div>

          <h4 className="section-subhead">
            Valores Óptimos de las Variables de Decisión:
          </h4>
          <div className="variables-grid">
            {solution &&
              Object.entries(solution).map(([variable, val]) => (
                <div key={variable} className="variable-card">
                  <div className="variable-name">{variable}</div>
                  <div className="variable-val">{formatFraction(val, showDecimal)}</div>
                </div>
              ))}
          </div>

          {/* Soluciones alternativas en caso de óptimos múltiples */}
          {special_cases?.has_multiple_optima &&
            special_cases.alternative_solutions?.length > 0 && (
              <div style={{ marginTop: '1.25rem' }}>
                <h4 className="section-subhead">Vértices Óptimos Alternativos Detectados:</h4>
                <div className="alt-solutions-list">
                  {special_cases.alternative_solutions.map((altSol, idx) => (
                    <div key={idx} className="alt-solution-pill">
                      <strong>Alternativa {idx + 1}:</strong>{' '}
                      <span className="mono-inline">
                        {Object.entries(altSol)
                          .map(([k, v]) => `${k} = ${formatFraction(v, showDecimal)}`)
                          .join(', ')}
                      </span>{' '}
                      (Z = {formatFraction(objective_value, showDecimal)})
                    </div>
                  ))}
                </div>
              </div>
            )}

          {/* Holgura o Exceso de cada restricción (Requisito 1.c) */}
          {constraint_results.length > 0 && (
            <div style={{ marginTop: '1.5rem' }}>
              <h4 className="section-subhead">
                Holgura o Exceso de Cada Restricción:
              </h4>
              <div className="modern-table-wrapper">
                <table className="modern-table">
                  <thead>
                    <tr>
                      <th>Restricción</th>
                      <th>Evaluación (LHS)</th>
                      <th>Sentido</th>
                      <th>Lado Derecho (RHS)</th>
                      <th>Holgura / Exceso</th>
                      <th>Estado</th>
                    </tr>
                  </thead>
                  <tbody>
                    {constraint_results.map((cr) => (
                      <tr key={cr.constraint_index}>
                        <td><strong>R<sub>{cr.constraint_index}</sub></strong></td>
                        <td className="mono-cell">{formatFraction(cr.lhs_value, showDecimal)}</td>
                        <td className="mono-cell" style={{ textAlign: 'center' }}>
                          {cr.sense === '<=' ? '≤' : cr.sense === '>=' ? '≥' : '='}
                        </td>
                        <td className="mono-cell">{formatFraction(cr.rhs_value, showDecimal)}</td>
                        <td className="mono-cell">
                          {formatFraction(cr.slack_or_surplus, showDecimal)}{' '}
                          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontFamily: 'var(--font-sans)' }}>
                            ({cr.type}{cr.variable_name ? `: ${cr.variable_name}` : ''})
                          </span>
                        </td>
                        <td>
                          <span className={`badge-inline ${cr.is_binding ? 'badge-success' : 'badge-neutral'}`}>
                            {cr.is_binding ? 'Activa (Saturada)' : 'No activa'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </Card>
  );
}
