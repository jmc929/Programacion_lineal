import React from 'react';
import { Card } from '../common/Card';

export function StandardFormCard({ standardForm }) {
  if (!standardForm) return null;

  return (
    <Card
      title="Forma Estándar del Problema"
      subtitle="Transformación del modelo con variables de holgura, exceso y artificiales"
      className="standard-form-card"
    >
      <div className="sf-objective-box">
        <div>
          <div className="sf-label">Función Objetivo Original</div>
          <div className="sf-eq">{standardForm.original_objective}</div>
        </div>
        <div>
          <div className="sf-label">Función Objetivo en Forma Estándar</div>
          <div className="sf-eq sf-eq-primary">{standardForm.standard_objective}</div>
        </div>
        {standardForm.objective_note && (
          <p className="sf-note">{standardForm.objective_note}</p>
        )}
      </div>

      <div className="sf-vars-row">
        <div className="sf-var-group">
          <span className="sf-var-label">Decisión:</span>
          {standardForm.decision_variables.map((v) => (
            <span key={v} className="var-pill var-pill-decision">{v}</span>
          ))}
        </div>

        {standardForm.slack_variables.length > 0 && (
          <div className="sf-var-group">
            <span className="sf-var-label">Holgura (+s):</span>
            {standardForm.slack_variables.map((v) => (
              <span key={v} className="var-pill var-pill-slack">{v}</span>
            ))}
          </div>
        )}

        {standardForm.surplus_variables.length > 0 && (
          <div className="sf-var-group">
            <span className="sf-var-label">Exceso (-e):</span>
            {standardForm.surplus_variables.map((v) => (
              <span key={v} className="var-pill var-pill-surplus">{v}</span>
            ))}
          </div>
        )}

        {standardForm.artificial_variables.length > 0 && (
          <div className="sf-var-group">
            <span className="sf-var-label">Artificiales (+a):</span>
            {standardForm.artificial_variables.map((v) => (
              <span key={v} className="var-pill var-pill-artificial">{v}</span>
            ))}
          </div>
        )}

        {standardForm.initial_basis.length > 0 && (
          <div className="sf-var-group">
            <span className="sf-var-label">Base Inicial:</span>
            <span className="var-pill var-pill-basis">
              {'{'}{standardForm.initial_basis.join(', ')}{'}'}
            </span>
          </div>
        )}
      </div>

      {standardForm.constraints && standardForm.constraints.length > 0 && (
        <div className="modern-table-wrapper" style={{ marginTop: '1rem' }}>
          <table className="modern-table">
            <thead>
              <tr>
                <th>Restr.</th>
                <th>Restricción Original</th>
                <th>Ecuación Estándar</th>
                <th>Transformación Aplicada</th>
              </tr>
            </thead>
            <tbody>
              {standardForm.constraints.map((c) => (
                <tr key={c.index}>
                  <td><strong>R<sub>{c.index}</sub></strong></td>
                  <td className="mono-cell">{c.original_equation}</td>
                  <td className="mono-cell">{c.standard_equation}</td>
                  <td style={{ fontSize: '0.88rem', color: 'var(--text-secondary)' }}>
                    {c.flipped && <span className="badge-inline badge-warn">RHS negativo invertido</span>}{' '}
                    {c.note}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Card>
  );
}
