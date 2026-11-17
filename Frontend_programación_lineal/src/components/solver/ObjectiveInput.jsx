import React from 'react';

export function ObjectiveInput({
  objective,
  direction,
  onDirectionChange,
  onCoefficientChange,
}) {
  return (
    <div className="objective-input-container">
      <div className="direction-selector">
        <label>Objetivo:</label>
        <select
          value={direction}
          onChange={(e) => onDirectionChange(e.target.value)}
        >
          <option value="max">Maximizar (Z)</option>
          <option value="min">Minimizar (Z)</option>
        </select>
      </div>

      <div className="coefficients-row">
        <span>Z = </span>
        {objective.map((coef, index) => (
          <span key={index} className="term">
            <input
              type="text"
              value={coef}
              placeholder="0"
              onChange={(e) => onCoefficientChange(index, e.target.value)}
              className="coef-input"
            />
            <span className="var-label">
              x{index + 1}
              {index < objective.length - 1 ? ' + ' : ''}
            </span>
          </span>
        ))}
      </div>
    </div>
  );
}
