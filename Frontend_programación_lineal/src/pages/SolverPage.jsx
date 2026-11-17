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
  const [variableCount, setVariableCount] = useState(2);
  const [direction, setDirection] = useState('max');
  const [method, setMethod] = useState('big_m');
  const [objective, setObjective] = useState(['3', '2']);
  const [constraints, setConstraints] = useState([
    { coefficients: ['1', '1'], sense: '<=', rhs: '4' },
    { coefficients: ['1', '0'], sense: '<=', rhs: '2' },
    { coefficients: ['0', '1'], sense: '<=', rhs: '3' },
  ]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const handleVariableCountChange = (count) => {
    const newCount = Math.max(1, count);
    setVariableCount(newCount);

    setObjective((prev) => {
      const updated = [...prev];
      while (updated.length < newCount) updated.push('0');
      return updated.slice(0, newCount);
    });

    setConstraints((prev) =>
      prev.map((c) => {
        const coefs = [...c.coefficients];
        while (coefs.length < newCount) coefs.push('0');
        return { ...c, coefficients: coefs.slice(0, newCount) };
      })
    );
  };

  const handleObjectiveCoefChange = (idx, val) => {
    setObjective((prev) => {
      const copy = [...prev];
      copy[idx] = val;
      return copy;
    });
  };

  const handleConstraintCoefChange = (cIdx, vIdx, val) => {
    setConstraints((prev) => {
      const copy = [...prev];
      const coefs = [...copy[cIdx].coefficients];
      coefs[vIdx] = val;
      copy[cIdx] = { ...copy[cIdx], coefficients: coefs };
      return copy;
    });
  };

  const handleConstraintSenseChange = (cIdx, sense) => {
    setConstraints((prev) => {
      const copy = [...prev];
      copy[cIdx] = { ...copy[cIdx], sense };
      return copy;
    });
  };

  const handleConstraintRhsChange = (cIdx, rhs) => {
    setConstraints((prev) => {
      const copy = [...prev];
      copy[cIdx] = { ...copy[cIdx], rhs };
      return copy;
    });
  };

  const handleAddConstraint = () => {
    setConstraints((prev) => [
      ...prev,
      { coefficients: Array(variableCount).fill('0'), sense: '<=', rhs: '0' },
    ]);
  };

  const handleRemoveConstraint = (idx) => {
    setConstraints((prev) => prev.filter((_, i) => i !== idx));
  };

  const handleSolve = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const payload = {
        objective,
        constraints,
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
        <p>Configura los parámetros, define el sistema de ecuaciones y optimiza con precisión exacta.</p>
      </div>

      <Card title="Parámetros del Problema">
        <div className="config-grid">
          <div className="form-group">
            <label className="form-label">Cantidad de Variables de Decisión</label>
            <input
              type="number"
              min="1"
              max="20"
              className="form-input"
              value={variableCount}
              onChange={(e) => handleVariableCountChange(parseInt(e.target.value) || 1)}
            />
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

        <ObjectiveInput
          objective={objective}
          direction={direction}
          onDirectionChange={setDirection}
          onCoefficientChange={handleObjectiveCoefChange}
        />

        <ConstraintList
          constraints={constraints}
          variableCount={variableCount}
          onCoefficientChange={handleConstraintCoefChange}
          onSenseChange={handleConstraintSenseChange}
          onRhsChange={handleConstraintRhsChange}
          onAddConstraint={handleAddConstraint}
          onRemoveConstraint={handleRemoveConstraint}
        />

        <div className="action-bar">
          <Button variant="primary" onClick={handleSolve} disabled={loading}>
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
