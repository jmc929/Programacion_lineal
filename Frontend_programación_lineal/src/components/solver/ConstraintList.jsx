import React from 'react';
import { Button } from '../common/Button';

export function ConstraintList({
  constraints,
  variableCount,
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
          <span>Restricciones del Sistema</span>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.2rem', fontWeight: 'normal' }}>
            Añade únicamente las variables que intervienen en cada restricción (sin necesidad de poner 0).
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
        {constraints.map((constraint, cIndex) => (
          <div key={cIndex} className="constraint-card-row">
            {/* Cabecera / Identificador de la restricción */}
            <div className="constraint-main-content">
              <span className="constraint-index">R<sub>{cIndex + 1}</sub>:</span>

              {/* Lista dinámica de variables que intervienen */}
              <div className="terms-wrapper">
                {constraint.terms.map((term, tIndex) => (
                  <React.Fragment key={tIndex}>
                    <div className="term-chip">
                      <input
                        type="text"
                        value={term.coefficient}
                        placeholder="1"
                        onChange={(e) =>
                          onTermCoefficientChange(cIndex, tIndex, e.target.value)
                        }
                        className="term-input"
                        title="Coeficiente de la variable (por defecto 1)"
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
                          <option key={i} value={i}>
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
                ))}

                {/* Botón para añadir otra variable a esta misma restricción */}
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

            {/* Operador y Lado Derecho (RHS) */}
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
                className="rhs-input"
                title="Valor del término independiente (Lado derecho)"
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
        ))}
      </div>
    </div>
  );
}
