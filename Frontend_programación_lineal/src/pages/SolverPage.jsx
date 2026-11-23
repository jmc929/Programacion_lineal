import React, { useRef, useState } from 'react';
import { Card, Button, Alert } from '../components/common';
import {
  ObjectiveInput,
  ConstraintList,
  SolutionSummary,
  IterationsTable,
  StandardFormCard,
  GraphicalMethod,
  SensitivityAnalysis,
  MethodComparison,
} from '../components/solver';
import {
  solveLinearProblem,
  compareLinearMethods,
  exportSolutionPdf,
} from '../services/api';
import { validateRationalInput } from '../utils/formatters';
import {
  EXAMPLE_PROBLEMS,
  exportProblemToCsv,
  exportProblemToJson,
  parseProblemFile,
} from '../utils/problemIO';

export function SolverPage() {
  const fileInputRef = useRef(null);

  const [variableCountInput, setVariableCountInput] = useState('2');
  const [variableCount, setVariableCount] = useState(2);
  const parsedCount = parseInt(variableCountInput.trim(), 10);
  const isValidVarCount =
    /^[1-9]\d*$/.test(variableCountInput.trim()) && parsedCount >= 1 && parsedCount <= 50;

  const [direction, setDirection] = useState('max');
  const [method, setMethod] = useState('big_m'); // 'big_m' | 'revised_simplex' | 'compare'
  const [mode, setMode] = useState('step_by_step'); // 'step_by_step' | 'direct'
  const [showDecimal, setShowDecimal] = useState(false);

  // Problema inicial (Ejemplo 1 de la guía)
  const [objectiveTerms, setObjectiveTerms] = useState([
    { varIndex: 0, coefficient: '50' },
    { varIndex: 1, coefficient: '80' },
  ]);

  const [constraints, setConstraints] = useState([
    {
      terms: [
        { varIndex: 0, coefficient: '2' },
        { varIndex: 1, coefficient: '1' },
      ],
      sense: '<=',
      rhs: '100',
    },
    {
      terms: [
        { varIndex: 0, coefficient: '1' },
        { varIndex: 1, coefficient: '3' },
      ],
      sense: '<=',
      rhs: '90',
    },
    {
      terms: [{ varIndex: 1, coefficient: '1' }],
      sense: '<=',
      rhs: '40',
    },
  ]);

  const [loading, setLoading] = useState(false);
  const [exportingPdf, setExportingPdf] = useState(false);
  const [error, setError] = useState(null);
  const [notice, setNotice] = useState(null);
  const [invalidFields, setInvalidFields] = useState({});

  const [result, setResult] = useState(null);
  const [comparisonData, setComparisonData] = useState(null);
  const [lastPayload, setLastPayload] = useState(null);
  const [activeTab, setActiveTab] = useState('steps');

  // --- Manejo de variables ---
  const applyNewVariableCount = (newCount) => {
    setVariableCount(newCount);
    setObjectiveTerms((prev) => {
      const valid = prev.filter((t) => t.varIndex < newCount);
      return valid.length > 0 ? valid : [{ varIndex: 0, coefficient: '1' }];
    });
    setConstraints((prev) =>
      prev.map((c) => {
        const valid = c.terms.filter((t) => t.varIndex < newCount);
        return {
          ...c,
          terms: valid.length > 0 ? valid : [{ varIndex: 0, coefficient: '1' }],
        };
      })
    );
  };

  const handleVariableCountInputChange = (e) => {
    const rawVal = e.target.value;
    setVariableCountInput(rawVal);
    const num = parseInt(rawVal.trim(), 10);
    if (/^[1-9]\d*$/.test(rawVal.trim()) && num >= 1 && num <= 50) {
      applyNewVariableCount(num);
    }
  };

  const handleQuickAddVariable = () => {
    if (variableCount >= 50) return;
    const nextCount = variableCount + 1;
    setVariableCountInput(String(nextCount));
    applyNewVariableCount(nextCount);
  };

  const handleQuickRemoveVariable = () => {
    if (variableCount <= 1) return;
    const nextCount = variableCount - 1;
    setVariableCountInput(String(nextCount));
    applyNewVariableCount(nextCount);
  };

  // --- Handlers Función Objetivo ---
  const handleAddObjectiveTerm = () => {
    setObjectiveTerms((prev) => {
      const usedVars = new Set(prev.map((t) => t.varIndex));
      let nextVar = 0;
      for (let i = 0; i < variableCount; i++) {
        if (!usedVars.has(i)) {
          nextVar = i;
          break;
        }
      }
      return [...prev, { varIndex: nextVar, coefficient: '1' }];
    });
  };

  const handleRemoveObjectiveTerm = (tIndex) => {
    setObjectiveTerms((prev) => prev.filter((_, i) => i !== tIndex));
  };

  const handleObjectiveTermCoefficientChange = (tIndex, val) => {
    setInvalidFields((prev) => {
      if (!prev[`obj-${tIndex}`]) return prev;
      const next = { ...prev };
      delete next[`obj-${tIndex}`];
      return next;
    });
    setObjectiveTerms((prev) => {
      const copy = [...prev];
      copy[tIndex] = { ...copy[tIndex], coefficient: val };
      return copy;
    });
  };

  const handleObjectiveTermVariableChange = (tIndex, newVarIndex) => {
    setObjectiveTerms((prev) => {
      const copy = [...prev];
      copy[tIndex] = { ...copy[tIndex], varIndex: newVarIndex };
      return copy;
    });
  };

  // --- Handlers Restricciones ---
  const handleAddConstraint = () => {
    setConstraints((prev) => [
      ...prev,
      {
        terms: [{ varIndex: 0, coefficient: '1' }],
        sense: '<=',
        rhs: '0',
      },
    ]);
  };

  const handleRemoveConstraint = (cIndex) => {
    setConstraints((prev) => prev.filter((_, i) => i !== cIndex));
  };

  const handleAddConstraintTerm = (cIndex) => {
    setConstraints((prev) => {
      const copy = [...prev];
      const target = { ...copy[cIndex] };
      const usedVars = new Set(target.terms.map((t) => t.varIndex));
      let nextVar = 0;
      for (let i = 0; i < variableCount; i++) {
        if (!usedVars.has(i)) {
          nextVar = i;
          break;
        }
      }
      target.terms = [...target.terms, { varIndex: nextVar, coefficient: '1' }];
      copy[cIndex] = target;
      return copy;
    });
  };

  const handleRemoveConstraintTerm = (cIndex, tIndex) => {
    setConstraints((prev) => {
      const copy = [...prev];
      const target = { ...copy[cIndex] };
      target.terms = target.terms.filter((_, i) => i !== tIndex);
      copy[cIndex] = target;
      return copy;
    });
  };

  const handleConstraintTermCoefficientChange = (cIndex, tIndex, value) => {
    setInvalidFields((prev) => {
      if (!prev[`c-${cIndex}-${tIndex}`]) return prev;
      const next = { ...prev };
      delete next[`c-${cIndex}-${tIndex}`];
      return next;
    });
    setConstraints((prev) => {
      const copy = [...prev];
      const target = { ...copy[cIndex] };
      const terms = [...target.terms];
      terms[tIndex] = { ...terms[tIndex], coefficient: value };
      target.terms = terms;
      copy[cIndex] = target;
      return copy;
    });
  };

  const handleConstraintTermVariableChange = (cIndex, tIndex, newVarIndex) => {
    setConstraints((prev) => {
      const copy = [...prev];
      const target = { ...copy[cIndex] };
      const terms = [...target.terms];
      terms[tIndex] = { ...terms[tIndex], varIndex: newVarIndex };
      target.terms = terms;
      copy[cIndex] = target;
      return copy;
    });
  };

  const handleConstraintSenseChange = (cIndex, sense) => {
    setConstraints((prev) => {
      const copy = [...prev];
      copy[cIndex] = { ...copy[cIndex], sense };
      return copy;
    });
  };

  const handleConstraintRhsChange = (cIndex, rhs) => {
    setInvalidFields((prev) => {
      if (!prev[`rhs-${cIndex}`]) return prev;
      const next = { ...prev };
      delete next[`rhs-${cIndex}`];
      return next;
    });
    setConstraints((prev) => {
      const copy = [...prev];
      copy[cIndex] = { ...copy[cIndex], rhs };
      return copy;
    });
  };

  // --- Validación estricta y construcción del payload ---
  const buildValidatedPayload = (overrideMethod, overrideMode) => {
    if (!isValidVarCount) {
      throw new Error('Define una cantidad válida de variables (número entero entre 1 y 50).');
    }

    const invalids = {};
    const errors = [];

    // Validar función objetivo
    const objSeen = new Set();
    const objectiveVector = Array(variableCount).fill('0');
    objectiveTerms.forEach((term, tIndex) => {
      if (objSeen.has(term.varIndex)) {
        invalids[`obj-${tIndex}`] = true;
        errors.push(`Función objetivo: la variable x${term.varIndex + 1} está repetida.`);
      }
      objSeen.add(term.varIndex);

      const check = validateRationalInput(term.coefficient);
      if (!check.valid) {
        invalids[`obj-${tIndex}`] = true;
        errors.push(`Función objetivo (x${term.varIndex + 1}): ${check.error}.`);
      } else {
        objectiveVector[term.varIndex] = String(term.coefficient).trim();
      }
    });

    // Validar restricciones
    const formattedConstraints = constraints.map((c, cIndex) => {
      const cSeen = new Set();
      const coefficients = Array(variableCount).fill('0');
      c.terms.forEach((term, tIndex) => {
        if (cSeen.has(term.varIndex)) {
          invalids[`c-${cIndex}-${tIndex}`] = true;
          errors.push(`Restricción R${cIndex + 1}: la variable x${term.varIndex + 1} está repetida.`);
        }
        cSeen.add(term.varIndex);

        const check = validateRationalInput(term.coefficient);
        if (!check.valid) {
          invalids[`c-${cIndex}-${tIndex}`] = true;
          errors.push(`Restricción R${cIndex + 1} (x${term.varIndex + 1}): ${check.error}.`);
        } else {
          coefficients[term.varIndex] = String(term.coefficient).trim();
        }
      });

      const rhsCheck = validateRationalInput(c.rhs);
      if (!rhsCheck.valid) {
        invalids[`rhs-${cIndex}`] = true;
        errors.push(`Restricción R${cIndex + 1} (lado derecho RHS): ${rhsCheck.error}.`);
      }

      return {
        coefficients,
        sense: c.sense,
        rhs: String(c.rhs).trim(),
      };
    });

    setInvalidFields(invalids);
    if (errors.length > 0) {
      throw new Error(errors.slice(0, 3).join(' '));
    }

    const effectiveMethod = overrideMethod || (method === 'compare' ? 'big_m' : method);
    const effectiveMode = overrideMode || mode;

    return {
      objective: objectiveVector,
      constraints: formattedConstraints,
      direction,
      method: effectiveMethod,
      mode: effectiveMode,
      max_iterations: 1000,
    };
  };

  // --- Cargar Ejemplo ---
  const handleLoadExample = (exampleId) => {
    const example = EXAMPLE_PROBLEMS.find((ex) => ex.id === exampleId);
    if (!example) return;
    setVariableCount(example.variableCount);
    setVariableCountInput(String(example.variableCount));
    setDirection(example.direction);
    setObjectiveTerms(example.objectiveTerms.map((t) => ({ ...t })));
    setConstraints(
      example.constraints.map((c) => ({
        terms: c.terms.map((t) => ({ ...t })),
        sense: c.sense,
        rhs: c.rhs,
      }))
    );
    setInvalidFields({});
    setError(null);
    setNotice(`Ejemplo cargado: ${example.name}`);
  };

  // --- Importar / Exportar JSON & CSV ---
  const handleExportJson = () => {
    try {
      buildValidatedPayload();
      exportProblemToJson({ variableCount, direction, method, objectiveTerms, constraints });
      setNotice('Problema guardado en problema_pl.json.');
      setError(null);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleExportCsv = () => {
    try {
      buildValidatedPayload();
      exportProblemToCsv({ variableCount, direction, objectiveTerms, constraints });
      setNotice('Problema guardado en problema_pl.csv.');
      setError(null);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleFileImport = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      try {
        const imported = parseProblemFile(file.name, String(reader.result || ''));
        setVariableCount(imported.variableCount);
        setVariableCountInput(String(imported.variableCount));
        setDirection(imported.direction);
        if (imported.method) setMethod(imported.method);
        setObjectiveTerms(imported.objectiveTerms);
        setConstraints(
          imported.constraints.length > 0
            ? imported.constraints
            : [{ terms: [{ varIndex: 0, coefficient: '1' }], sense: '<=', rhs: '0' }]
        );
        setInvalidFields({});
        setError(null);
        setNotice(`Archivo "${file.name}" cargado correctamente.`);
      } catch (err) {
        setError(err.message || 'No se pudo leer el archivo seleccionado.');
      }
    };
    reader.readAsText(file);
    e.target.value = '';
  };

  // --- Enviar a Resolver ---
  const handleSolve = async (forcedMode = null) => {
    setError(null);
    setNotice(null);

    let payload;
    try {
      payload = buildValidatedPayload(null, forcedMode);
    } catch (validationErr) {
      setError(validationErr.message);
      return;
    }

    setLoading(true);
    try {
      if (method === 'compare') {
        const data = await compareLinearMethods(payload);
        setComparisonData(data);
        setResult(data.big_m);
        setLastPayload({ ...payload, method: 'big_m', mode: 'step_by_step' });
        setActiveTab('compare');
      } else {
        const data = await solveLinearProblem(payload);
        setComparisonData(null);
        setResult(data);
        setLastPayload(payload);
        if (payload.mode === 'step_by_step') {
          setActiveTab('steps');
        } else {
          setActiveTab('graphical');
        }
      }
    } catch (err) {
      setError(err.message || 'Error al comunicarse con el servidor.');
    } finally {
      setLoading(false);
    }
  };

  // --- Exportar a PDF ---
  const handleExportPdf = async () => {
    if (!lastPayload) return;
    setExportingPdf(true);
    setError(null);
    try {
      await exportSolutionPdf({ ...lastPayload, mode: 'step_by_step' });
      setNotice('Reporte paso a paso exportado a PDF correctamente.');
    } catch (err) {
      setError(err.message || 'Error al exportar el PDF.');
    } finally {
      setExportingPdf(false);
    }
  };

  const hasStepByStep = result && result.mode === 'step_by_step' && result.iterations?.length > 0;

  return (
    <div className="page-container solver-page">
      <div className="page-header">
        <h2>Solucionador de Modelos Lineales</h2>
        <p>
          Resuelve modelos con Gran M y Simplex Revisado usando fracciones exactas, método gráfico y análisis de sensibilidad.
        </p>
      </div>

      {/* Barra de Ejemplos y Carga/Guardado JSON/CSV */}
      <div className="io-toolbar">
        <div className="io-toolbar-left">
          <label className="io-label">Ejemplos de evaluación:</label>
          <select
            className="form-select io-select"
            defaultValue=""
            onChange={(e) => {
              if (e.target.value) handleLoadExample(e.target.value);
              e.target.value = '';
            }}
          >
            <option value="">-- Cargar un ejemplo del proyecto --</option>
            {EXAMPLE_PROBLEMS.map((ex) => (
              <option key={ex.id} value={ex.id}>
                {ex.name}
              </option>
            ))}
          </select>
        </div>

        <div className="io-toolbar-right">
          <input
            ref={fileInputRef}
            type="file"
            accept=".json,.csv"
            onChange={handleFileImport}
            style={{ display: 'none' }}
          />
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={() => fileInputRef.current?.click()}
            title="Cargar problema desde un archivo JSON o CSV"
          >
            📂 Cargar JSON / CSV
          </button>
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={handleExportJson}
            title="Guardar el problema actual en formato JSON"
          >
            💾 Guardar JSON
          </button>
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={handleExportCsv}
            title="Guardar el problema actual en formato CSV"
          >
            📄 Guardar CSV
          </button>
        </div>
      </div>

      {notice && (
        <div className="alert alert-info">
          <span>ℹ️ {notice}</span>
        </div>
      )}

      <Card title="Parámetros del Problema">
        <div className="config-grid">
          <div className="form-group">
            <label className="form-label">Cantidad de Variables de Decisión</label>
            <div style={{ display: 'flex', gap: '0.4rem', alignItems: 'flex-start' }}>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={handleQuickRemoveVariable}
                disabled={variableCount <= 1}
                title="Quitar la última variable"
                style={{ padding: '0.6rem 0.8rem' }}
              >
                −
              </button>
              <div style={{ flex: 1 }}>
                <input
                  type="text"
                  className={`form-input ${!isValidVarCount ? 'input-error' : ''}`}
                  value={variableCountInput}
                  onChange={handleVariableCountInputChange}
                  placeholder="Ej. 2"
                  style={{ width: '100%', textAlign: 'center', fontFamily: 'var(--font-mono)', fontWeight: 700 }}
                />
                {!isValidVarCount && (
                  <span className="field-error-msg">
                    ⚠️ Entero entre 1 y 50
                  </span>
                )}
              </div>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={handleQuickAddVariable}
                disabled={variableCount >= 50}
                title="Añadir una variable adicional"
                style={{ whiteSpace: 'nowrap', padding: '0.6rem 0.85rem' }}
              >
                + x{variableCount + 1}
              </button>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Método Algorítmico</label>
            <select
              className="form-select"
              value={method}
              onChange={(e) => setMethod(e.target.value)}
            >
              <option value="big_m">Método de la Gran M (Tableau Simplex)</option>
              <option value="revised_simplex">Simplex Revisado (Dos Fases Matricial)</option>
              <option value="compare">Comparar Ambos (Gran M vs. Simplex Revisado)</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Modo de Solución</label>
            <select
              className="form-select"
              value={method === 'compare' ? 'step_by_step' : mode}
              disabled={method === 'compare'}
              onChange={(e) => setMode(e.target.value)}
            >
              <option value="step_by_step">Paso a paso (forma estándar + iteraciones)</option>
              <option value="direct">Solución directa (solo resultado final)</option>
            </select>
          </div>
        </div>

        <ObjectiveInput
          objectiveTerms={objectiveTerms}
          direction={direction}
          variableCount={variableCount}
          invalidFields={invalidFields}
          onDirectionChange={setDirection}
          onAddTerm={handleAddObjectiveTerm}
          onRemoveTerm={handleRemoveObjectiveTerm}
          onTermCoefficientChange={handleObjectiveTermCoefficientChange}
          onTermVariableChange={handleObjectiveTermVariableChange}
        />

        <ConstraintList
          constraints={constraints}
          variableCount={variableCount}
          invalidFields={invalidFields}
          onAddConstraint={handleAddConstraint}
          onRemoveConstraint={handleRemoveConstraint}
          onAddTerm={handleAddConstraintTerm}
          onRemoveTerm={handleRemoveConstraintTerm}
          onTermCoefficientChange={handleConstraintTermCoefficientChange}
          onTermVariableChange={handleConstraintTermVariableChange}
          onSenseChange={handleConstraintSenseChange}
          onRhsChange={handleConstraintRhsChange}
        />

        <div className="action-bar">
          <Button
            variant="primary"
            onClick={() => handleSolve()}
            disabled={loading || !isValidVarCount}
          >
            {loading
              ? 'Calculando solución exacta...'
              : method === 'compare'
              ? '⚖️ Resolver y Comparar Ambos Métodos'
              : '⚡ Resolver Modelo'}
          </Button>
        </div>
      </Card>

      {error && <Alert type="danger" message={error} />}

      {result && (
        <div className="results-workspace">
          {/* Barra de acciones sobre resultados */}
          <div className="results-action-strip">
            <label className="decimal-toggle">
              <input
                type="checkbox"
                checked={showDecimal}
                onChange={(e) => setShowDecimal(e.target.checked)}
              />
              <span>Mostrar equivalencia decimal junto a fracciones exactas</span>
            </label>

            <Button
              variant="secondary"
              onClick={handleExportPdf}
              disabled={exportingPdf}
              style={{ padding: '0.5rem 1rem', fontSize: '0.88rem' }}
            >
              {exportingPdf ? 'Generando PDF...' : '📥 Exportar Paso a Paso a PDF'}
            </Button>
          </div>

          {/* Resumen de solución siempre visible */}
          <SolutionSummary result={result} showDecimal={showDecimal} />

          {/* Navegación clara por secciones de análisis */}
          <div className="results-tabs-bar">
            {comparisonData && (
              <button
                type="button"
                className={`result-tab-btn ${activeTab === 'compare' ? 'active' : ''}`}
                onClick={() => setActiveTab('compare')}
              >
                ⚖️ Comparación de Métodos
              </button>
            )}

            {!comparisonData && (
              <button
                type="button"
                className={`result-tab-btn ${activeTab === 'steps' ? 'active' : ''}`}
                onClick={() => {
                  if (!hasStepByStep) {
                    setMode('step_by_step');
                    handleSolve('step_by_step');
                  } else {
                    setActiveTab('steps');
                  }
                }}
              >
                📝 Paso a Paso {hasStepByStep ? `(${result.iterations.length})` : '(activar)'}
              </button>
            )}

            <button
              type="button"
              className={`result-tab-btn ${activeTab === 'graphical' ? 'active' : ''}`}
              onClick={() => setActiveTab('graphical')}
            >
              📐 Método Gráfico {result.graphical?.applicable ? '(2D)' : '(N/A)'}
            </button>

            <button
              type="button"
              className={`result-tab-btn ${activeTab === 'sensitivity' ? 'active' : ''}`}
              onClick={() => setActiveTab('sensitivity')}
            >
              📊 Análisis de Sensibilidad
            </button>
          </div>

          {/* Contenido de la pestaña activa */}
          {activeTab === 'compare' && comparisonData && (
            <MethodComparison comparisonData={comparisonData} showDecimal={showDecimal} />
          )}

          {activeTab === 'steps' && !comparisonData && (
            hasStepByStep ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                <StandardFormCard standardForm={result.standard_form} />
                <IterationsTable
                  iterations={result.iterations}
                  method={result.method}
                  showDecimal={showDecimal}
                />
              </div>
            ) : (
              <Card title="Modo Solución Directa">
                <p style={{ color: 'var(--text-secondary)', marginBottom: '1rem' }}>
                  El problema se resolvió en modo de solución directa (solo resultado). Si deseas inspeccionar la forma estándar y cada iteración, cambia a modo paso a paso.
                </p>
                <Button
                  variant="primary"
                  onClick={() => {
                    setMode('step_by_step');
                    handleSolve('step_by_step');
                  }}
                >
                  Ver Proceso Paso a Paso
                </Button>
              </Card>
            )
          )}

          {activeTab === 'graphical' && (
            <GraphicalMethod graphical={result.graphical} showDecimal={showDecimal} />
          )}

          {activeTab === 'sensitivity' && (
            <SensitivityAnalysis sensitivity={result.sensitivity} showDecimal={showDecimal} />
          )}
        </div>
      )}
    </div>
  );
}
