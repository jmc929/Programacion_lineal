import React, { useState } from 'react';
import { Card, Button, Alert } from '../components/common';
import {
  ObjectiveInput,
  ConstraintList,
  SolutionSummary,
  IterationsTable,
} from '../components/solver';
import { solveLinearProblem } from '../services/api';

export function SolverPage() {
  // Manejo de la cantidad de variables permitiendo borrar el texto completamente
  const [variableCountInput, setVariableCountInput] = useState('2');
  const [variableCount, setVariableCount] = useState(2);
  const isValidVarCount = /^[1-9]\d*$/.test(variableCountInput.trim());

  const [direction, setDirection] = useState('max');
  const [method, setMethod] = useState('big_m');

  // Función objetivo dinámica: solo las variables que intervienen (sin tener que poner 0)
  const [objectiveTerms, setObjectiveTerms] = useState([
    { varIndex: 0, coefficient: '3' },
    { varIndex: 1, coefficient: '2' },
  ]);

  // Restricciones dinámicas: solo las variables que intervienen (sin tener que poner 0)
  const [constraints, setConstraints] = useState([
    {
      terms: [
        { varIndex: 0, coefficient: '1' },
        { varIndex: 1, coefficient: '1' },
      ],
      sense: '<=',
      rhs: '4',
    },
    {
      terms: [{ varIndex: 0, coefficient: '1' }],
      sense: '<=',
      rhs: '2',
    },
    {
      terms: [{ varIndex: 1, coefficient: '1' }],
      sense: '<=',
      rhs: '3',
    },
  ]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  // Manejador del input de cantidad de variables (permite borrar libremente)
  const handleVariableCountInputChange = (e) => {
    const rawVal = e.target.value;
    setVariableCountInput(rawVal);

    const num = parseInt(rawVal, 10);
    if (!isNaN(num) && num >= 1 && num <= 50) {
      applyNewVariableCount(num);
    }
  };

  // Botón rápido para añadir una variable adicional
  const handleQuickAddVariable = () => {
    const nextCount = variableCount + 1;
    setVariableCountInput(String(nextCount));
    applyNewVariableCount(nextCount);
  };

  const applyNewVariableCount = (newCount) => {
    setVariableCount(newCount);

    // Filtrar términos de función objetivo que queden fuera de rango
    setObjectiveTerms((prev) => {
      const valid = prev.filter((t) => t.varIndex < newCount);
      return valid.length > 0 ? valid : [{ varIndex: 0, coefficient: '1' }];
    });

    // Filtrar términos de restricciones que queden fuera de rango
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
    setConstraints((prev) => {
      const copy = [...prev];
      copy[cIndex] = { ...copy[cIndex], rhs };
      return copy;
    });
  };

  // --- Enviar a Resolver ---
  const handleSolve = async () => {
    if (!isValidVarCount) {
      setError('Por favor define una cantidad válida de variables (número entero mayor a 0).');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      // 1. Armar vector de función objetivo (por defecto '0' para las variables que no participan)
      const objectiveVector = Array(variableCount).fill('0');
      for (const term of objectiveTerms) {
        if (term.varIndex >= 0 && term.varIndex < variableCount) {
          const raw = term.coefficient?.trim();
          objectiveVector[term.varIndex] = raw === '' || raw === undefined ? '1' : raw;
        }
      }

      // 2. Armar matriz de restricciones (por defecto '0' para las variables que no participan)
      const formattedConstraints = constraints.map((c) => {
        const coefficients = Array(variableCount).fill('0');
        for (const term of c.terms) {
          if (term.varIndex >= 0 && term.varIndex < variableCount) {
            const raw = term.coefficient?.trim();
            coefficients[term.varIndex] = raw === '' || raw === undefined ? '1' : raw;
          }
        }
        return {
          coefficients,
          sense: c.sense,
          rhs: c.rhs?.trim() === '' ? '0' : c.rhs?.trim() || '0',
        };
      });

      const payload = {
        objective: objectiveVector,
        constraints: formattedConstraints,
        direction,
        method,
        max_iterations: 1000,
      };

      const data = await solveLinearProblem(payload);
      setResult(data);
    } catch (err) {
      setError(err.message || 'Error al comunicarse con el servidor.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container solver-page">
      <div className="page-header">
        <h2>Solucionador de Modelos Lineales</h2>
        <p>Configura las variables y restricciones directamente con solo los términos que participan.</p>
      </div>

      <Card title="Parámetros del Problema">
        <div className="config-grid">
          <div className="form-group">
            <label className="form-label">Cantidad de Variables de Decisión</label>
            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'flex-start' }}>
              <div style={{ flex: 1 }}>
                <input
                  type="text"
                  className={`form-input ${!isValidVarCount ? 'input-error' : ''}`}
                  value={variableCountInput}
                  onChange={handleVariableCountInputChange}
                  placeholder="Ej. 2"
                  style={{ width: '100%' }}
                />
                {!isValidVarCount && (
                  <span className="field-error-msg">
                    ⚠️ Debe llenarse con un número mayor a 0
                  </span>
                )}
              </div>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={handleQuickAddVariable}
                title="Añadir una variable más (x3, x4...)"
                style={{ whiteSpace: 'nowrap', padding: '0.65rem 0.9rem' }}
              >
                + Añadir x{variableCount + 1}
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
            </select>
          </div>
        </div>

        {/* Función Objetivo Dinámica */}
        <ObjectiveInput
          objectiveTerms={objectiveTerms}
          direction={direction}
          variableCount={variableCount}
          onDirectionChange={setDirection}
          onAddTerm={handleAddObjectiveTerm}
          onRemoveTerm={handleRemoveObjectiveTerm}
          onTermCoefficientChange={handleObjectiveTermCoefficientChange}
          onTermVariableChange={handleObjectiveTermVariableChange}
        />

        {/* Lista de Restricciones Dinámicas */}
        <ConstraintList
          constraints={constraints}
          variableCount={variableCount}
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
            onClick={handleSolve}
            disabled={loading || !isValidVarCount}
          >
            {loading ? 'Calculando solución exacta...' : '⚡ Resolver Modelo'}
          </Button>
        </div>
      </Card>

      {error && <Alert type="danger" message={error} />}

      {result && (
        <>
          <SolutionSummary result={result} />
          <IterationsTable iterations={result.iterations} method={method} />
        </>
      )}
    </div>
  );
}
