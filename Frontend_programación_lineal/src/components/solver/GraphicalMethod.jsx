import React, { useState } from 'react';
import { Card } from '../common/Card';
import { formatFraction } from '../../utils/formatters';

const LINE_COLORS = [
  '#2563eb', // blue
  '#059669', // emerald
  '#ea580c', // orange
  '#9333ea', // purple
  '#e11d48', // rose
  '#0891b2', // cyan
  '#ca8a04', // yellow-amber
  '#4f46e5', // indigo
];

function formatTick(val) {
  if (Math.abs(val) < 1e-9) return '0';
  if (Number.isInteger(val)) return String(val);
  return Number(val.toFixed(2)).toString();
}

export function GraphicalMethod({ graphical, showDecimal = false }) {
  const [hoveredVertex, setHoveredVertex] = useState(null);

  if (!graphical) return null;

  if (!graphical.applicable) {
    return (
      <Card title="Método Gráfico" className="graphical-card">
        <div className="info-banner">
          <span className="info-banner-icon">📐</span>
          <div>
            <strong>Método gráfico no aplicable</strong>
            <p>{graphical.message}</p>
          </div>
        </div>
      </Card>
    );
  }

  const {
    region_type,
    bounds,
    feasible_polygon = [],
    vertices = [],
    constraint_lines = [],
    objective_line,
    optimal_segment = [],
    message,
  } = graphical;

  const width = 680;
  const height = 450;
  const padLeft = 64;
  const padRight = 36;
  const padTop = 30;
  const padBottom = 52;
  const plotW = width - padLeft - padRight;
  const plotH = height - padTop - padBottom;

  const xMax = Math.max(bounds?.x_max || 10, 1e-6);
  const yMax = Math.max(bounds?.y_max || 10, 1e-6);

  const mapX = (x) => padLeft + (x / xMax) * plotW;
  const mapY = (y) => padTop + plotH - (y / yMax) * plotH;

  const tickCount = 5;
  const xTicks = Array.from({ length: tickCount + 1 }, (_, i) => (i / tickCount) * xMax);
  const yTicks = Array.from({ length: tickCount + 1 }, (_, i) => (i / tickCount) * yMax);

  const polygonPointsAttr = feasible_polygon
    .map((p) => `${mapX(p.x1_float).toFixed(2)},${mapY(p.x2_float).toFixed(2)}`)
    .join(' ');

  const regionBadgeMap = {
    bounded: { label: 'Región Factible Acotada', cls: 'status-optimal' },
    unbounded: { label: 'Región Factible No Acotada', cls: 'status-unbounded' },
    empty: { label: 'Región Factible Vacía (Infactible)', cls: 'status-infeasible' },
    segment: { label: 'Región Factible: Segmento de Recta (Igualdad)', cls: 'status-optimal' },
    point: { label: 'Región Factible: Punto Único', cls: 'status-optimal' },
  };
  const badge = regionBadgeMap[region_type] || { label: region_type, cls: '' };

  return (
    <Card
      title="Método Gráfico (2 Variables)"
      subtitle="Región factible, restricciones rotuladas, vértices evaluados y recta de isoutilidad / isocosto"
      className="graphical-card"
    >
      <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
        <span className={`status-badge ${badge.cls}`} style={{ marginBottom: 0 }}>
          {badge.label}
        </span>
        <span style={{ color: 'var(--text-secondary)', fontSize: '0.92rem' }}>
          {message}
        </span>
      </div>

      <div className="graph-layout">
        <div className="graph-svg-wrapper">
          <svg
            viewBox={`0 0 ${width} ${height}`}
            className="graph-svg"
            role="img"
            aria-label="Plano cartesiano del método gráfico de programación lineal"
          >
            <defs>
              <pattern id="feasibleHatch" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
                <line x1="0" y1="0" x2="0" y2="10" stroke="rgba(79, 70, 229, 0.22)" strokeWidth="2" />
              </pattern>
              <clipPath id="plotClip">
                <rect x={padLeft} y={padTop} width={plotW} height={plotH} />
              </clipPath>
            </defs>

            {/* Fondo del plano */}
            <rect
              x={padLeft}
              y={padTop}
              width={plotW}
              height={plotH}
              fill="#f8fafc"
              stroke="#e2e8f0"
              strokeWidth="1"
            />

            {/* Cuadrícula */}
            {xTicks.map((tx, i) => (
              <g key={`xg-${i}`}>
                <line
                  x1={mapX(tx)}
                  y1={padTop}
                  x2={mapX(tx)}
                  y2={padTop + plotH}
                  stroke="#e2e8f0"
                  strokeWidth="1"
                />
                <text
                  x={mapX(tx)}
                  y={padTop + plotH + 18}
                  textAnchor="middle"
                  fontSize="11"
                  fill="#64748b"
                  fontFamily="var(--font-mono)"
                >
                  {formatTick(tx)}
                </text>
              </g>
            ))}

            {yTicks.map((ty, i) => (
              <g key={`yg-${i}`}>
                <line
                  x1={padLeft}
                  y1={mapY(ty)}
                  x2={padLeft + plotW}
                  y2={mapY(ty)}
                  stroke="#e2e8f0"
                  strokeWidth="1"
                />
                <text
                  x={padLeft - 10}
                  y={mapY(ty) + 4}
                  textAnchor="end"
                  fontSize="11"
                  fill="#64748b"
                  fontFamily="var(--font-mono)"
                >
                  {formatTick(ty)}
                </text>
              </g>
            ))}

            {/* Región Factible */}
            <g clipPath="url(#plotClip)">
              {feasible_polygon.length >= 3 && (
                <>
                  <polygon
                    points={polygonPointsAttr}
                    fill="rgba(79, 70, 229, 0.16)"
                    stroke="#4f46e5"
                    strokeWidth={region_type === 'unbounded' ? '1.5' : '2'}
                    strokeDasharray={region_type === 'unbounded' ? '6 4' : undefined}
                  />
                  <polygon points={polygonPointsAttr} fill="url(#feasibleHatch)" />
                </>
              )}

              {feasible_polygon.length === 2 && (
                <line
                  x1={mapX(feasible_polygon[0].x1_float)}
                  y1={mapY(feasible_polygon[0].x2_float)}
                  x2={mapX(feasible_polygon[1].x1_float)}
                  y2={mapY(feasible_polygon[1].x2_float)}
                  stroke="#4f46e5"
                  strokeWidth="5"
                  strokeLinecap="round"
                />
              )}

              {/* Rectas de restricciones */}
              {constraint_lines.map((line, idx) => {
                if (!line.points || line.points.length < 2) return null;
                const color = LINE_COLORS[idx % LINE_COLORS.length];
                const [p0, p1] = line.points;
                const x1 = mapX(p0.x1_float);
                const y1 = mapY(p0.x2_float);
                const x2 = mapX(p1.x1_float);
                const y2 = mapY(p1.x2_float);
                // Posición escalonada para evitar superposición de etiquetas
                const t = 0.25 + ((idx * 0.19) % 0.55);
                const lx = x1 + t * (x2 - x1);
                const ly = y1 + t * (y2 - y1);

                return (
                  <g key={`line-${line.label}`}>
                    <line
                      x1={x1}
                      y1={y1}
                      x2={x2}
                      y2={y2}
                      stroke={color}
                      strokeWidth="2.2"
                    />
                    <rect
                      x={lx - 14}
                      y={ly - 11}
                      width="28"
                      height="17"
                      rx="5"
                      fill="#ffffff"
                      stroke={color}
                      strokeWidth="1.2"
                    />
                    <text
                      x={lx}
                      y={ly + 1}
                      textAnchor="middle"
                      fontSize="10"
                      fontWeight="700"
                      fill={color}
                      fontFamily="var(--font-mono)"
                    >
                      {line.label}
                    </text>
                  </g>
                );
              })}

              {/* Recta de isoutilidad / función objetivo en el óptimo */}
              {objective_line && objective_line.points?.length >= 2 && (
                <g>
                  <line
                    x1={mapX(objective_line.points[0].x1_float)}
                    y1={mapY(objective_line.points[0].x2_float)}
                    x2={mapX(objective_line.points[1].x1_float)}
                    y2={mapY(objective_line.points[1].x2_float)}
                    stroke="#dc2626"
                    strokeWidth="2.5"
                    strokeDasharray="8 5"
                  />
                </g>
              )}

              {/* Segmento óptimo resaltado para soluciones óptimas múltiples */}
              {optimal_segment.length === 2 && (
                <line
                  x1={mapX(optimal_segment[0].x1_float)}
                  y1={mapY(optimal_segment[0].x2_float)}
                  x2={mapX(optimal_segment[1].x1_float)}
                  y2={mapY(optimal_segment[1].x2_float)}
                  stroke="#059669"
                  strokeWidth="5.5"
                  strokeLinecap="round"
                />
              )}
            </g>

            {/* Ejes principales */}
            <line
              x1={padLeft}
              y1={padTop + plotH}
              x2={padLeft + plotW}
              y2={padTop + plotH}
              stroke="#0f172a"
              strokeWidth="2"
            />
            <line
              x1={padLeft}
              y1={padTop}
              x2={padLeft}
              y2={padTop + plotH}
              stroke="#0f172a"
              strokeWidth="2"
            />
            <text
              x={padLeft + plotW / 2}
              y={height - 10}
              textAnchor="middle"
              fontSize="13"
              fontWeight="700"
              fill="#0f172a"
            >
              x₁
            </text>
            <text
              x={18}
              y={padTop + plotH / 2}
              textAnchor="middle"
              fontSize="13"
              fontWeight="700"
              fill="#0f172a"
              transform={`rotate(-90 18 ${padTop + plotH / 2})`}
            >
              x₂
            </text>

            {/* Aviso visual dentro del gráfico para región vacía o no acotada */}
            {region_type === 'empty' && (
              <g>
                <rect
                  x={padLeft + plotW / 2 - 115}
                  y={padTop + plotH / 2 - 22}
                  width="230"
                  height="44"
                  rx="10"
                  fill="rgba(254, 242, 242, 0.95)"
                  stroke="#ef4444"
                  strokeWidth="1.5"
                />
                <text
                  x={padLeft + plotW / 2}
                  y={padTop + plotH / 2 + 5}
                  textAnchor="middle"
                  fontSize="13"
                  fontWeight="700"
                  fill="#991b1b"
                >
                  Región factible vacía (Infactible)
                </text>
              </g>
            )}

            {region_type === 'unbounded' && (
              <g>
                <rect
                  x={padLeft + plotW - 158}
                  y={padTop + 10}
                  width="148"
                  height="26"
                  rx="7"
                  fill="rgba(255, 251, 235, 0.95)"
                  stroke="#f59e0b"
                  strokeWidth="1.2"
                />
                <text
                  x={padLeft + plotW - 84}
                  y={padTop + 27}
                  textAnchor="middle"
                  fontSize="11"
                  fontWeight="700"
                  fill="#92400e"
                >
                  ↗ Región no acotada
                </text>
              </g>
            )}

            {/* Vértices y etiquetas */}
            {vertices.map((v, idx) => {
              const cx = mapX(v.x1_float);
              const cy = mapY(v.x2_float);
              const isHovered = hoveredVertex === idx;
              const labelX = cx > padLeft + plotW - 135 ? cx - 10 : cx + 10;
              const anchor = cx > padLeft + plotW - 135 ? 'end' : 'start';
              const labelY = cy < padTop + 26 ? cy + 16 : cy - 10;

              return (
                <g
                  key={`v-${idx}`}
                  style={{ cursor: 'pointer' }}
                  onMouseEnter={() => setHoveredVertex(idx)}
                  onMouseLeave={() => setHoveredVertex(null)}
                >
                  {v.is_optimal && (
                    <circle
                      cx={cx}
                      cy={cy}
                      r={isHovered ? 12 : 10}
                      fill="rgba(16, 185, 129, 0.22)"
                      stroke="#059669"
                      strokeWidth="1.5"
                    />
                  )}
                  <circle
                    cx={cx}
                    cy={cy}
                    r={v.is_optimal ? 6 : isHovered ? 6 : 4.5}
                    fill={v.is_optimal ? '#059669' : '#1e293b'}
                    stroke="#ffffff"
                    strokeWidth="1.8"
                  />
                  <text
                    x={labelX}
                    y={labelY}
                    textAnchor={anchor}
                    fontSize="10.5"
                    fontWeight={v.is_optimal ? '800' : '600'}
                    fill={v.is_optimal ? '#065f46' : '#0f172a'}
                    fontFamily="var(--font-mono)"
                    paintOrder="stroke"
                    stroke="#ffffff"
                    strokeWidth="3.5"
                    strokeLinejoin="round"
                  >
                    ({v.x1}, {v.x2}) Z={v.z}
                  </text>
                </g>
              );
            })}
          </svg>
        </div>

        {/* Leyenda lateral */}
        <div className="graph-legend">
          <h4>Leyenda de Rectas</h4>
          <ul className="legend-list">
            {feasible_polygon.length >= 2 && (
              <li className="legend-item">
                <span className="legend-swatch legend-swatch-region" />
                <span>Región factible (x₁ ≥ 0, x₂ ≥ 0)</span>
              </li>
            )}
            {constraint_lines.map((line, idx) => (
              <li key={line.label} className="legend-item">
                <span
                  className="legend-swatch"
                  style={{ backgroundColor: LINE_COLORS[idx % LINE_COLORS.length] }}
                />
                <span>
                  <strong>{line.label}:</strong>{' '}
                  <code className="mono-inline">{line.equation}</code>
                </span>
              </li>
            ))}
            {objective_line && (
              <li className="legend-item">
                <span className="legend-swatch legend-swatch-iso" />
                <span>
                  <strong>Recta Óptima:</strong>{' '}
                  <code className="mono-inline">{objective_line.equation}</code>
                </span>
              </li>
            )}
            {optimal_segment.length === 2 && (
              <li className="legend-item">
                <span className="legend-swatch" style={{ backgroundColor: '#059669' }} />
                <span>
                  <strong>Segmento Óptimo Múltiple</strong>
                </span>
              </li>
            )}
          </ul>
        </div>
      </div>

      {/* Tabla de vértices */}
      {vertices.length > 0 && (
        <div style={{ marginTop: '1.5rem' }}>
          <h4 style={{ marginBottom: '0.75rem', color: 'var(--text-secondary)' }}>
            Vértices de la Región Factible y Evaluación de Z
          </h4>
          <div className="modern-table-wrapper">
            <table className="modern-table">
              <thead>
                <tr>
                  <th>Vértice</th>
                  <th>x₁</th>
                  <th>x₂</th>
                  <th>Valor de Z</th>
                  <th>Evaluación</th>
                </tr>
              </thead>
              <tbody>
                {vertices.map((v, idx) => (
                  <tr key={idx} className={v.is_optimal ? 'row-optimal' : ''}>
                    <td><strong>V<sub>{idx + 1}</sub></strong></td>
                    <td className="mono-cell">{formatFraction(v.x1, showDecimal)}</td>
                    <td className="mono-cell">{formatFraction(v.x2, showDecimal)}</td>
                    <td className="mono-cell">{formatFraction(v.z, showDecimal)}</td>
                    <td>
                      {v.is_optimal ? (
                        <span className="badge-inline badge-success">★ Óptimo</span>
                      ) : (
                        <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Factible</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </Card>
  );
}
