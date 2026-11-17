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
    <div className="constraints-container">
      <div className="constraints-header">
        <h4>Restricciones del Problema</h4>
        <Button variant="secondary" onClick={onAddConstraint}>
          + Agregar Restricción
        </Button>
      </div>

      <div className="constraints-list">
        {constraints.map((constraint, cIndex) => (
          <div key={cIndex} className="constraint-row">
            <span className="constraint-number">R{cIndex + 1}:</span>
            <div className="terms-container">
              {constraint.coefficients.map((coef, vIndex) => (
                <span key={vIndex} className="term">
                  <input
                    type="text"
                    value={coef}
                    placeholder="0"
                    onChange={(e) =>
                      onCoefficientChange(cIndex, vIndex, e.target.value)
                    }
                    className="coef-input"
                  />
                  <span className="var-label">
                    x{vIndex + 1}
                    {vIndex < variableCount - 1 ? ' + ' : ''}
                  </span>
                </span>
              ))}
            </div>

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
              placeholder="RHS"
              onChange={(e) => onRhsChange(cIndex, e.target.value)}
              className="rhs-input"
            />

            {constraints.length > 1 && (
              <Button
                variant="danger"
                onClick={() => onRemoveConstraint(cIndex)}
                title="Eliminar restricción"
              >
                &times;
              </Button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
