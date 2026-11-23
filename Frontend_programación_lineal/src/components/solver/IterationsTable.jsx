import React, { useEffect, useState } from 'react';
import { Card } from '../common/Card';
import { formatBigMCost, formatFraction } from '../../utils/formatters';

function IterationDetailView({ iter, method, showDecimal }) {
  const isBigM = method === 'big_m' || iter.tableau !== null;
  const pivot = iter.pivot;
  const vnames = iter.variable_names || Object.keys(iter.reduced_costs || {});
  const ratioMap = {};
  (iter.ratio_test || []).forEach((entry) => {
    ratioMap[entry.row] = entry;
  });

  return (
    <div className="iteration-detail-panel">
      {/* Metadatos de la iteración */}
      <div className="iteration-meta-grid">
        <div className="meta-box">
          <div className="meta-box-label">Base Actual (B)</div>
          <div className="meta-box-value">
            {'{'}{iter.basic_variables.join(', ')}{'}'}
          </div>
        </div>
        <div className="meta-box">
          <div className="meta-box-label">Valor de Z</div>
          <div className="meta-box-value" style={{ color: 'var(--primary)' }}>
            {formatFraction(iter.objective_value, showDecimal)}
          </div>
        </div>
        {iter.big_m_objective && (
          <div className="meta-box">
            <div className="meta-box-label">Objetivo Penalizado (Gran M)</div>
            <div className="meta-box-value">
              {formatBigMCost(iter.big_m_objective, showDecimal)}
            </div>
          </div>
        )}
        {iter.phase && iter.phase_objective_value !== null && iter.phase_objective_value !== undefined && (
          <div className="meta-box">
            <div className="meta-box-label">Objetivo Fase {iter.phase}</div>
            <div className="meta-box-value">
              {formatFraction(iter.phase_objective_value, showDecimal)}
            </div>
          </div>
        )}
        <div className="meta-box">
          <div className="meta-box-label">Variable Entrante</div>
          <div className="meta-box-value" style={{ color: iter.entering_variable ? 'var(--success-dark)' : 'var(--text-muted)' }}>
            {iter.entering_variable ? `↓ ${iter.entering_variable}` : 'Ninguna (Fin)'}
          </div>
        </div>
        <div className="meta-box">
          <div className="meta-box-label">Variable Saliente</div>
          <div className="meta-box-value" style={{ color: iter.leaving_variable ? 'var(--danger-dark)' : 'var(--text-muted)' }}>
            {iter.leaving_variable ? `↑ ${iter.leaving_variable}` : 'Ninguna'}
          </div>
        </div>
        {pivot && (
          <div className="meta-box meta-box-pivot">
            <div className="meta-box-label">Elemento Pivote</div>
            <div className="meta-box-value" style={{ color: 'var(--primary)' }}>
              {formatFraction(pivot.value, showDecimal)}{' '}
              <span style={{ fontSize: '0.78rem', fontWeight: 500, color: 'var(--text-muted)' }}>
                (fila {pivot.row + 1}, {pivot.col_variable})
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Justificación de las decisiones en la iteración */}
      {(iter.entering_reason || iter.leaving_reason) && (
        <div className="justification-box">
          <div className="justification-title">Justificación de la Iteración {iter.iteration}{iter.phase ? ` (Fase ${iter.phase})` : ''}</div>
          {iter.entering_reason && (
            <p><strong>Criterio de entrada / parada:</strong> {iter.entering_reason}</p>
          )}
          {iter.leaving_reason && (
            <p><strong>Criterio de salida (razón mínima):</strong> {iter.leaving_reason}</p>
          )}
          {iter.is_degenerate && (
            <p className="degenerate-tag">⚡ Iteración degenerada: al menos una variable básica tiene valor 0.</p>
          )}
        </div>
      )}

      {/* TABLERO COMPLETO — GRAN M */}
      {isBigM && iter.tableau && (
        <div style={{ marginTop: '1.25rem' }}>
          <h4 className="section-subhead">Tablero Simplex (Gran M)</h4>
          <div className="modern-table-wrapper">
            <table className="modern-table tableau-table">
              <thead>
                <tr>
                  <th>Base</th>
                  {vnames.map((vn) => (
                    <th
                      key={vn}
                      className={iter.entering_variable === vn ? 'col-entering-head' : ''}
                    >
                      {vn}
                      {iter.entering_variable === vn && ' ↓'}
                    </th>
                  ))}
                  <th>RHS (b<sub>i</sub>)</th>
                  {iter.ratio_test && iter.ratio_test.length > 0 && <th>Razón Mínima</th>}
                </tr>
              </thead>
              <tbody>
                {iter.tableau.map((row, rIdx) => {
                  const isPivotRow = pivot && pivot.row === rIdx;
                  const rt = ratioMap[rIdx];
                  return (
                    <tr key={rIdx} className={isPivotRow ? 'row-leaving' : ''}>
                      <td>
                        <strong>{iter.basic_variables[rIdx]}</strong>
                        {isPivotRow && ' ↑'}
                      </td>
                      {row.slice(0, vnames.length).map((cell, cIdx) => {
                        const isPivotCol = pivot && pivot.col === cIdx;
                        const isPivotCell = isPivotRow && isPivotCol;
                        return (
                          <td
                            key={cIdx}
                            className={`mono-cell ${
                              isPivotCell
                                ? 'cell-pivot'
                                : isPivotCol
                                ? 'col-entering'
                                : ''
                            }`}
                          >
                            {formatFraction(cell, showDecimal)}
                          </td>
                        );
                      })}
                      <td className="mono-cell">
                        <strong>{formatFraction(row[row.length - 1], showDecimal)}</strong>
                      </td>
                      {iter.ratio_test && iter.ratio_test.length > 0 && (
                        <td className={`mono-cell ${rt?.is_minimum ? 'cell-min-ratio' : ''}`}>
                          {rt
                            ? rt.eligible
                              ? `${formatFraction(rt.rhs)} / ${formatFraction(rt.pivot_column_value)} = ${formatFraction(rt.ratio, showDecimal)}${rt.is_minimum ? ' ★' : ''}`
                              : 'No aplica (≤ 0)'
                            : '—'}
                        </td>
                      )}
                    </tr>
                  );
                })}
                {/* Fila Cj - Zj (Costos Reducidos) */}
                <tr className="row-reduced-costs">
                  <td><strong>C<sub>j</sub> − Z<sub>j</sub></strong></td>
                  {vnames.map((vn) => (
                    <td
                      key={`rc-${vn}`}
                      className={`mono-cell ${iter.entering_variable === vn ? 'col-entering' : ''}`}
                    >
                      {formatBigMCost(iter.reduced_costs?.[vn], showDecimal)}
                    </td>
                  ))}
                  <td className="mono-cell">
                    <strong>
                      {iter.big_m_objective
                        ? formatBigMCost(iter.big_m_objective, showDecimal)
                        : formatFraction(iter.objective_value, showDecimal)}
                    </strong>
                  </td>
                  {iter.ratio_test && iter.ratio_test.length > 0 && <td>—</td>}
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* MATRIZ B^-1, COSTOS REDUCIDOS Y RAZÓN MÍNIMA — SIMPLEX REVISADO */}
      {!isBigM && (
        <div className="revised-grid">
          {/* Matriz B^-1 y valores básicos */}
          {iter.inverse_basis && iter.inverse_basis.length > 0 && (
            <div>
              <h4 className="section-subhead">
                Inversa de la Base (B<sup>-1</sup>) y Solución Básica (x<sub>B</sub> = B<sup>-1</sup>b)
              </h4>
              <div className="modern-table-wrapper">
                <table className="modern-table">
                  <thead>
                    <tr>
                      <th>Var. Básica</th>
                      {iter.inverse_basis[0].map((_, cIdx) => (
                        <th key={cIdx}>Col {cIdx + 1}</th>
                      ))}
                      <th>x<sub>B</sub></th>
                    </tr>
                  </thead>
                  <tbody>
                    {iter.inverse_basis.map((row, rIdx) => (
                      <tr key={rIdx} className={pivot && pivot.row === rIdx ? 'row-leaving' : ''}>
                        <td><strong>{iter.basic_variables[rIdx]}</strong></td>
                        {row.map((val, cIdx) => (
                          <td key={cIdx} className="mono-cell">
                            {formatFraction(val, showDecimal)}
                          </td>
                        ))}
                        <td className="mono-cell">
                          <strong>{formatFraction(iter.basic_values[rIdx], showDecimal)}</strong>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {iter.dual_values && iter.dual_values.length > 0 && (
                <div className="dual-strip">
                  <strong>Multiplicadores Simplex (y<sup>T</sup> = c<sub>B</sub><sup>T</sup>B<sup>-1</sup>):</strong>{' '}
                  <span className="mono-inline">
                    [{iter.dual_values.map((v) => formatFraction(v, showDecimal)).join(', ')}]
                  </span>
                </div>
              )}
            </div>
          )}

          {/* Costos Reducidos */}
          <div>
            <h4 className="section-subhead">Costos Reducidos (c̄<sub>j</sub> = c<sub>j</sub> − y<sup>T</sup>A<sub>j</sub>)</h4>
            <div className="modern-table-wrapper">
              <table className="modern-table">
                <thead>
                  <tr>
                    {vnames.map((vn) => (
                      <th
                        key={`rh-${vn}`}
                        className={iter.entering_variable === vn ? 'col-entering-head' : ''}
                      >
                        {vn}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    {vnames.map((vn) => (
                      <td
                        key={`rv-${vn}`}
                        className={`mono-cell ${iter.entering_variable === vn ? 'col-entering' : ''}`}
                      >
                        {formatBigMCost(iter.reduced_costs?.[vn], showDecimal)}
                      </td>
                    ))}
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* Prueba de la razón mínima con vector dirección d = B^-1 a_j */}
          {iter.ratio_test && iter.ratio_test.length > 0 && (
            <div>
              <h4 className="section-subhead">
                Prueba de la Razón Mínima (Dirección d = B<sup>-1</sup>a<sub>{iter.entering_variable}</sub>)
              </h4>
              <div className="modern-table-wrapper">
                <table className="modern-table">
                  <thead>
                    <tr>
                      <th>Var. Básica</th>
                      <th>Valor (x<sub>B</sub>)</th>
                      <th>Dirección (d<sub>i</sub>)</th>
                      <th>Razón (x<sub>B,i</sub> / d<sub>i</sub>)</th>
                      <th>Decisión</th>
                    </tr>
                  </thead>
                  <tbody>
                    {iter.ratio_test.map((rt) => (
                      <tr key={rt.row} className={rt.is_minimum ? 'row-leaving' : ''}>
                        <td><strong>{rt.basic_variable}</strong></td>
                        <td className="mono-cell">{formatFraction(rt.rhs, showDecimal)}</td>
                        <td className={`mono-cell ${rt.is_minimum ? 'cell-pivot' : ''}`}>
                          {formatFraction(rt.pivot_column_value, showDecimal)}
                        </td>
                        <td className="mono-cell">
                          {rt.eligible ? formatFraction(rt.ratio, showDecimal) : 'No aplica (dᵢ ≤ 0)'}
                        </td>
                        <td>
                          {rt.is_minimum ? (
                            <span className="badge-inline badge-danger">★ Mínima — Sale {rt.basic_variable}</span>
                          ) : rt.eligible ? (
                            <span className="badge-inline badge-neutral">Elegible</span>
                          ) : (
                            <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Descartada</span>
                          )}
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
    </div>
  );
}

export function IterationsTable({ iterations, method = 'big_m', showDecimal = false }) {
  const [selectedIteration, setSelectedIteration] = useState(0);
  const [viewAll, setViewAll] = useState(false);

  // Reiniciar la pestaña seleccionada cuando cambia el conjunto de iteraciones
  useEffect(() => {
    setSelectedIteration(0);
  }, [iterations]);

  if (!iterations || iterations.length === 0) return null;

  const currentIter = iterations[selectedIteration] || iterations[0];

  return (
    <Card
      title={`Evolución Paso a Paso (${iterations.length} ${iterations.length === 1 ? 'iteración' : 'iteraciones'})`}
      subtitle={
        method === 'revised_simplex'
          ? 'Inversa de la base B⁻¹, multiplicadores simplex, costos reducidos y prueba de la razón mínima'
          : 'Tablero Simplex completo, fila Cj − Zj, prueba de la razón mínima y elemento pivote'
      }
      className="iterations-card"
    >
      <div className="iterations-toolbar">
        <div className="iteration-tabs" style={{ marginBottom: 0, paddingBottom: 0 }}>
          {!viewAll &&
            iterations.map((iter, idx) => (
              <button
                key={idx}
                type="button"
                className={`tab-btn ${selectedIteration === idx ? 'active' : ''}`}
                onClick={() => setSelectedIteration(idx)}
              >
                Iteración {iter.iteration} {iter.phase ? `(Fase ${iter.phase})` : ''}
                {idx === iterations.length - 1 ? ' • Final' : ''}
              </button>
            ))}
        </div>

        <button
          type="button"
          className="btn btn-secondary"
          style={{ padding: '0.4rem 0.9rem', fontSize: '0.82rem', whiteSpace: 'nowrap' }}
          onClick={() => setViewAll((v) => !v)}
        >
          {viewAll ? 'Ver por pestañas' : 'Ver todas las iteraciones'}
        </button>
      </div>

      {viewAll ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', marginTop: '1.25rem' }}>
          {iterations.map((iter, idx) => (
            <div key={idx} className="iteration-all-block">
              <div className="iteration-all-header">
                Iteración {iter.iteration} {iter.phase ? `(Fase ${iter.phase})` : ''}
                {idx === iterations.length - 1 ? ' — Iteración Final' : ''}
              </div>
              <IterationDetailView iter={iter} method={method} showDecimal={showDecimal} />
            </div>
          ))}
        </div>
      ) : (
        <div style={{ marginTop: '1.25rem' }}>
          <IterationDetailView iter={currentIter} method={method} showDecimal={showDecimal} />
        </div>
      )}
    </Card>
  );
}
