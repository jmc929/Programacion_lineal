import React from 'react';

export function ObjectiveInput({
  objectiveTerms,
  direction,
  variableCount,
  onDirectionChange,
  onAddTerm,
  onRemoveTerm,
  onTermCoefficientChange,
  onTermVariableChange,
}) {
  return (
    <div className="builder-section">
      <div className="builder-title">
        <div>
          <span>Función Objetivo</span>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.2rem', fontWeight: 'normal' }}>
            Indica solo las variables que aportan a la función objetivo (no necesitas poner 0).
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <label className="form-label" style={{ margin: 0 }}>Criterio:</label>
          <select
            className="form-select"
            value={direction}
            onChange={(e) => onDirectionChange(e.target.value)}
          >
            <option value="max">Maximizar (Z)</option>
            <option value="min">Minimizar (Z)</option>
          </select>
        </div>
      </div>

      <div className="equation-row">
        <span className="equation-label">{direction.toUpperCase()} Z =</span>

        {objectiveTerms.map((term, tIndex) => (
          <React.Fragment key={tIndex}>
            <div className="term-chip">
              <input
                type="text"
                value={term.coefficient}
                placeholder="1"
                onChange={(e) => onTermCoefficientChange(tIndex, e.target.value)}
                className="term-input"
                title="Coeficiente (por defecto 1)"
              />

              <select
                value={term.varIndex}
                onChange={(e) =>
                  onTermVariableChange(tIndex, parseInt(e.target.value, 10))
                }
                className="term-var-select"
                title="Variable"
              >
                {Array.from({ length: variableCount }, (_, i) => (
                  <option key={i} value={i}>
                    x{i + 1}
                  </option>
                ))}
              </select>

              {objectiveTerms.length > 1 && (
                <button
                  type="button"
                  className="btn-remove-term"
                  onClick={() => onRemoveTerm(tIndex)}
                  title="Quitar esta variable de la función objetivo"
                >
                  &times;
                </button>
              )}
            </div>

            {tIndex < objectiveTerms.length - 1 && (
              <span className="math-operator">+</span>
            )}
          </React.Fragment>
        ))}

        {objectiveTerms.length < variableCount && (
          <button
            type="button"
            className="btn-add-term"
            onClick={onAddTerm}
            title="Añadir otra variable a la función objetivo"
          >
            + Variable
          </button>
        )}
      </div>
    </div>
  );
}
