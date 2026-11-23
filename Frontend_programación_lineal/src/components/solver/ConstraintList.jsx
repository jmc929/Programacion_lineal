import React from 'react';
import { Button } from '../common/Button';

export function ConstraintList({
  constraints,
  variableCount,
  invalidFields = {},
  onAddConstraint,
  onRemoveConstraint,
  onAddTerm,
  onRemoveTerm,
  onTermCoefficientChange,
  onTermVariableChange,
  onSenseChange,
  onRhsChange,
}) {
  return (
    <div className="builder-section" style={{ marginTop: '1.5rem' }}>
      <div className="builder-title">
        <div>
          <span>Restricciones del Sistema (x<sub>i</sub> ≥ 0)</span>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.2rem', fontWeight: 'normal' }}>
            Soporta ≤, ≥, = y lados derechos de cualquier signo (positivos, cero o negativos).
          </p>
        </div>
        <Button
          variant="secondary"
          onClick={onAddConstraint}
          style={{ padding: '0.45rem 1rem', fontSize: '0.875rem' }}
        >
          + Nueva Restricción
        </Button>
      </div>

      <div className="constraints-list">
        {constraints.map((constraint, cIndex) => {
          const usedVars = new Set(constraint.terms.map((t) => t.varIndex));
          const rhsInvalid = Boolean(invalidFields[`rhs-${cIndex}`]);

          return (
            <div key={cIndex} className="constraint-card-row">
              <div className="constraint-main-content">
                <span className="constraint-index">R<sub>{cIndex + 1}</sub>:</span>

                <div className="terms-wrapper">
                  {constraint.terms.map((term, tIndex) => {
                    const isInvalid = Boolean(invalidFields[`c-${cIndex}-${tIndex}`]);
                    return (
                      <React.Fragment key={tIndex}>
                        <div className={`term-chip ${isInvalid ? 'input-error' : ''}`}>
                          <input
                            type="text"
                            value={term.coefficient}
                            placeholder="coef"
                            onChange={(e) =>
                              onTermCoefficientChange(cIndex, tIndex, e.target.value)
                            }
                            className="term-input"
                            title="Coeficiente de la variable"
                          />

                          <select
                            value={term.varIndex}
                            onChange={(e) =>
                              onTermVariableChange(cIndex, tIndex, parseInt(e.target.value, 10))
                            }
                            className="term-var-select"
                            title="Seleccionar variable"
                          >
                            {Array.from({ length: variableCount }, (_, i) => (
                              <option
                                key={i}
                                value={i}
                                disabled={usedVars.has(i) && term.varIndex !== i}
                              >
                                x{i + 1}
                              </option>
                            ))}
                          </select>

                          {constraint.terms.length > 1 && (
                            <button
                              type="button"
                              className="btn-remove-term"
                              onClick={() => onRemoveTerm(cIndex, tIndex)}
                              title="Quitar esta variable de la restricción"
                            >
                              &times;
                            </button>
                          )}
                        </div>

                        {tIndex < constraint.terms.length - 1 && (
                          <span className="math-operator">+</span>
                        )}
                      </React.Fragment>
                    );
                  })}

                  {constraint.terms.length < variableCount && (
                    <button
                      type="button"
                      className="btn-add-term"
                      onClick={() => onAddTerm(cIndex)}
                      title="Añadir otra variable a esta restricción"
                    >
                      + Variable
                    </button>
                  )}
                </div>
              </div>

              <div className="constraint-right-controls">
                <select
                  value={constraint.sense}
                  onChange={(e) => onSenseChange(cIndex, e.target.value)}
                  className="sense-select"
                  title="Sentido de la desigualdad"
                >
                  <option value="<=">&le;</option>
                  <option value=">=">&ge;</option>
                  <option value="=">=</option>
                </select>

                <input
                  type="text"
                  value={constraint.rhs}
                  placeholder="RHS"
                  onChange={(e) => onRhsChange(cIndex, e.target.value)}
                  className={`rhs-input ${rhsInvalid ? 'input-error' : ''}`}
                  title="Valor del término independiente (puede ser negativo)"
                />

                {constraints.length > 1 && (
                  <button
                    type="button"
                    className="btn-remove-row"
                    onClick={() => onRemoveConstraint(cIndex)}
                    title="Eliminar esta restricción completa"
                  >
                    &times;
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
