import React, { useState } from 'react';
import { Card } from '../common/Card';
import { IterationsTable } from './IterationsTable';
import { StandardFormCard } from './StandardFormCard';

export function MethodComparison({ comparisonData, showDecimal = false }) {
  const [inspectMethod, setInspectMethod] = useState('big_m');

  if (!comparisonData) return null;
  const { big_m, revised_simplex, comparison } = comparisonData;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <Card
        title="Comparación: Gran M vs. Simplex Revisado"
        subtitle="Análisis comparativo de iteraciones, trayectoria de bases y consistencia de resultados"
      >
        <div className={`status-badge ${comparison.same_status && comparison.same_objective_value ? 'status-optimal' : 'status-unbounded'}`}>
          {comparison.same_status && comparison.same_objective_value
            ? '✓ Resultados Verificados y Consistentes entre Ambos Métodos'
            : '⚠ Revisar diferencias entre métodos'}
        </div>

        <p style={{ color: 'var(--text-secondary)', marginBottom: '1.25rem' }}>
          {comparison.summary}
        </p>

        <div className="iteration-meta-grid">
          <div className="meta-box">
            <div className="meta-box-label">Iteraciones Gran M</div>
            <div className="meta-box-value" style={{ color: 'var(--primary)' }}>
              {comparison.big_m_iterations}
            </div>
          </div>
          <div className="meta-box">
            <div className="meta-box-label">Iteraciones Simplex Revisado</div>
            <div className="meta-box-value" style={{ color: 'var(--accent)' }}>
              {comparison.revised_simplex_iterations}
              {comparison.revised_phase1_iterations > 0 && (
                <span style={{ fontSize: '0.78rem', fontWeight: 500, color: 'var(--text-muted)', marginLeft: '0.4rem' }}>
                  (F1: {comparison.revised_phase1_iterations}, F2: {comparison.revised_phase2_iterations})
                </span>
              )}
            </div>
          </div>
          <div className="meta-box">
            <div className="meta-box-label">Z* Gran M</div>
            <div className="meta-box-value">{big_m.objective_value ?? big_m.status}</div>
          </div>
          <div className="meta-box">
            <div className="meta-box-label">Z* Simplex Revisado</div>
            <div className="meta-box-value">{revised_simplex.objective_value ?? revised_simplex.status}</div>
          </div>
        </div>

        <h4 className="section-subhead">Comparación Iteración por Iteración</h4>
        <div className="modern-table-wrapper">
          <table className="modern-table">
            <thead>
              <tr>
                <th>Paso</th>
                <th>Gran M — Base</th>
                <th>Gran M — Entra / Sale</th>
                <th>Gran M — Z</th>
                <th>Revisado — Fase</th>
                <th>Revisado — Base</th>
                <th>Revisado — Entra / Sale</th>
                <th>Revisado — Z</th>
              </tr>
            </thead>
            <tbody>
              {comparison.steps.map((s) => (
                <tr key={s.step}>
                  <td><strong>{s.step}</strong></td>
                  <td className="mono-cell">{s.big_m_basis ? s.big_m_basis.join(', ') : '—'}</td>
                  <td className="mono-cell">
                    {s.big_m_entering
                      ? `↓${s.big_m_entering} / ↑${s.big_m_leaving ?? '—'}`
                      : s.big_m_basis ? 'Fin' : '—'}
                  </td>
                  <td className="mono-cell">{s.big_m_z ?? '—'}</td>
                  <td>{s.revised_phase ? `Fase ${s.revised_phase}` : s.revised_basis ? 'Directa' : '—'}</td>
                  <td className="mono-cell">{s.revised_basis ? s.revised_basis.join(', ') : '—'}</td>
                  <td className="mono-cell">
                    {s.revised_entering
                      ? `↓${s.revised_entering} / ↑${s.revised_leaving ?? '—'}`
                      : s.revised_basis ? 'Fin' : '—'}
                  </td>
                  <td className="mono-cell">{s.revised_z ?? '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div style={{ marginTop: '1.5rem', display: 'flex', gap: '0.6rem', flexWrap: 'wrap', alignItems: 'center' }}>
          <span style={{ fontWeight: 700, fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
            Inspeccionar paso a paso completo de:
          </span>
          <button
            type="button"
            className={`tab-btn ${inspectMethod === 'big_m' ? 'active' : ''}`}
            onClick={() => setInspectMethod('big_m')}
          >
            Método de la Gran M ({big_m.iterations.length} iter.)
          </button>
          <button
            type="button"
            className={`tab-btn ${inspectMethod === 'revised_simplex' ? 'active' : ''}`}
            onClick={() => setInspectMethod('revised_simplex')}
          >
            Simplex Revisado ({revised_simplex.iterations.length} iter.)
          </button>
        </div>
      </Card>

      {inspectMethod === 'big_m' ? (
        <>
          <StandardFormCard standardForm={big_m.standard_form} />
          <IterationsTable
            iterations={big_m.iterations}
            method="big_m"
            showDecimal={showDecimal}
          />
        </>
      ) : (
        <>
          <StandardFormCard standardForm={revised_simplex.standard_form} />
          <IterationsTable
            iterations={revised_simplex.iterations}
            method="revised_simplex"
            showDecimal={showDecimal}
          />
        </>
      )}
    </div>
  );
}
