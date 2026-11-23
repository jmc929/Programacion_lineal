import React from 'react';
import { Card } from '../common/Card';
import { formatBound, formatDelta, formatFraction } from '../../utils/formatters';

export function SensitivityAnalysis({ sensitivity, showDecimal = false }) {
  if (!sensitivity) return null;

  if (!sensitivity.applicable) {
    return (
      <Card title="Análisis de Sensibilidad" className="sensitivity-card">
        <div className="info-banner">
          <span className="info-banner-icon">📊</span>
          <div>
            <strong>Análisis de sensibilidad no aplicable</strong>
            <p>{sensitivity.message}</p>
          </div>
        </div>
      </Card>
    );
  }

  const { objective_ranges = [], rhs_ranges = [], notes = [] } = sensitivity;

  return (
    <Card
      title="Análisis de Sensibilidad"
      subtitle="Precios sombra, costos reducidos, rangos de optimalidad (cⱼ) y rangos de factibilidad (bᵢ)"
      className="sensitivity-card"
    >
      {/* 1. Coeficientes de la función objetivo y costos reducidos */}
      <h4 className="section-subhead">
        1. Coeficientes de la Función Objetivo (c<sub>j</sub>) y Costos Reducidos
      </h4>
      <div className="modern-table-wrapper">
        <table className="modern-table">
          <thead>
            <tr>
              <th>Variable</th>
              <th>Valor Óptimo</th>
              <th>Costo Reducido</th>
              <th>Coef. Actual (c<sub>j</sub>)</th>
              <th>Disminución Perm.</th>
              <th>Aumento Perm.</th>
              <th>Rango [Mín, Máx]</th>
            </tr>
          </thead>
          <tbody>
            {objective_ranges.map((item) => (
              <tr key={item.variable}>
                <td>
                  <strong>{item.variable}</strong>{' '}
                  <span className={`badge-inline ${item.is_basic ? 'badge-info' : 'badge-neutral'}`}>
                    {item.is_basic ? 'Básica' : 'No básica'}
                  </span>
                </td>
                <td className="mono-cell">{formatFraction(item.optimal_value, showDecimal)}</td>
                <td className="mono-cell">{formatFraction(item.reduced_cost, showDecimal)}</td>
                <td className="mono-cell">{formatFraction(item.current_coefficient, showDecimal)}</td>
                <td className="mono-cell">{formatDelta(item.allowable_decrease, showDecimal)}</td>
                <td className="mono-cell">{formatDelta(item.allowable_increase, showDecimal)}</td>
                <td className="mono-cell">
                  [{formatBound(item.min_value, true, showDecimal)}, {formatBound(item.max_value, false, showDecimal)}]
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="interpretation-box">
        <div className="interpretation-title">Interpretación — Coeficientes y Costos Reducidos</div>
        <ul>
          {objective_ranges.map((item) => (
            <li key={`int-obj-${item.variable}`}>{item.interpretation}</li>
          ))}
        </ul>
      </div>

      {/* 2. Precios sombra y rangos de lados derechos */}
      <h4 className="section-subhead" style={{ marginTop: '1.75rem' }}>
        2. Restricciones, Precios Sombra y Rangos del Lado Derecho (b<sub>i</sub>)
      </h4>
      {rhs_ranges.length === 0 ? (
        <p style={{ color: 'var(--text-muted)' }}>El problema no tiene restricciones.</p>
      ) : (
        <>
          <div className="modern-table-wrapper">
            <table className="modern-table">
              <thead>
                <tr>
                  <th>Restricción</th>
                  <th>Estado</th>
                  <th>Holgura / Exceso</th>
                  <th>Precio Sombra</th>
                  <th>RHS Actual (b<sub>i</sub>)</th>
                  <th>Disminución Perm.</th>
                  <th>Aumento Perm.</th>
                  <th>Rango [Mín, Máx]</th>
                </tr>
              </thead>
              <tbody>
                {rhs_ranges.map((item) => (
                  <tr key={item.constraint_index}>
                    <td><strong>R<sub>{item.constraint_index}</sub></strong> ({item.sense})</td>
                    <td>
                      <span className={`badge-inline ${item.is_binding ? 'badge-success' : 'badge-neutral'}`}>
                        {item.is_binding ? 'Activa' : 'No activa'}
                      </span>
                    </td>
                    <td className="mono-cell">
                      {formatFraction(item.slack_or_surplus, showDecimal)}{' '}
                      <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>({item.type})</span>
                    </td>
                    <td className="mono-cell" style={{ color: item.shadow_price !== '0' ? '#047857' : undefined }}>
                      {formatFraction(item.shadow_price, showDecimal)}
                    </td>
                    <td className="mono-cell">{formatFraction(item.current_rhs, showDecimal)}</td>
                    <td className="mono-cell">{formatDelta(item.allowable_decrease, showDecimal)}</td>
                    <td className="mono-cell">{formatDelta(item.allowable_increase, showDecimal)}</td>
                    <td className="mono-cell">
                      [{formatBound(item.min_value, true, showDecimal)}, {formatBound(item.max_value, false, showDecimal)}]
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="interpretation-box">
            <div className="interpretation-title">Interpretación — Precios Sombra y Lados Derechos</div>
            <ul>
              {rhs_ranges.map((item) => (
                <li key={`int-rhs-${item.constraint_index}`}>{item.interpretation}</li>
              ))}
            </ul>
          </div>
        </>
      )}

      {notes.length > 0 && (
        <div className="special-notice-box" style={{ marginTop: '1.25rem' }}>
          {notes.map((note, idx) => (
            <p key={idx}>⚠️ {note}</p>
          ))}
        </div>
      )}
    </Card>
  );
}
