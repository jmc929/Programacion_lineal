import React from 'react';
import { Button } from '../common/Button';

export function ConstraintList({
  constraints,
  variableCount,
  onCoefficientChange,
  onSenseChange,
  onRhsChange,
  onAddConstraint,
  onRemoveConstraint,
}) {
  return (
    <div className="builder-section" style={{ marginTop: '1.5rem' }}>
      <div className="builder-title">
        <span>Restricciones del Sistema</span>
        <Button variant="secondary" onClick={onAddConstraint} style={{ padding: '0.4rem 0.9rem', fontSize: '0.85rem' }}>
          + Añadir Restricción
        </Button>
      </div>

      <div className="constraints-list">
        {constraints.map((constraint, cIndex) => (
          <div key={cIndex} className="constraint-card-row">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
              <span className="constraint-index">R<sub>{cIndex + 1}</sub></span>
              <div className="equation-row">
                {constraint.coefficients.map((coef, vIndex) => (
                  <React.Fragment key={vIndex}>
                    <div className="math-term">
                      <input
                        type="text"
                        value={coef}
                        placeholder="0"
                        onChange={(e) =>
                          onCoefficientChange(cIndex, vIndex, e.target.value)
                        }
                        className="coef-input"
                      />
                      <span className="var-badge">x<sub>{vIndex + 1}</sub></span>
                    </div>
                    {vIndex < variableCount - 1 && (
                      <span className="math-operator">+</span>
                    )}
                  </React.Fragment>
                ))}
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <select
                value={constraint.sense}
                onChange={(e) => onSenseChange(cIndex, e.target.value)}
                className="sense-select"
              >
                <option value="<=">&le;</option>
                <option value=">=">&ge;</option>
                <option value="=">=</option>
              </select>

              <input
                type="text"
                value={constraint.rhs}
                placeholder="b"
                onChange={(e) => onRhsChange(cIndex, e.target.value)}
                className="rhs-input"
              />

              {constraints.length > 1 && (
                <button
                  type="button"
                  className="btn-remove-row"
                  onClick={() => onRemoveConstraint(cIndex)}
                  title="Eliminar fila"
                >
                  &times;
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
