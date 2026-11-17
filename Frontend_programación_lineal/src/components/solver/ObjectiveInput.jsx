import React from 'react';

export function ObjectiveInput({
  objective,
  direction,
  onDirectionChange,
  onCoefficientChange,
}) {
  return (
    <div className="builder-section">
      <div className="builder-title">
        <span>Función Objetivo</span>
        <div className="form-group" style={{ flexDirection: 'row', alignItems: 'center', gap: '0.5rem' }}>
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
        {objective.map((coef, index) => (
          <React.Fragment key={index}>
            <div className="math-term">
              <input
                type="text"
                value={coef}
                placeholder="0"
                onChange={(e) => onCoefficientChange(index, e.target.value)}
                className="coef-input"
              />
              <span className="var-badge">x<sub>{index + 1}</sub></span>
            </div>
            {index < objective.length - 1 && (
              <span className="math-operator">+</span>
            )}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
}
