import { useState } from 'react';
import { solveLinearProblem } from '../services/api';

export function useLinearSolver() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const solve = async (payload) => {
    setLoading(true);
    setError(null);
    try {
      const data = await solveLinearProblem(payload);
      setResult(data);
      return data;
    } catch (err) {
      setError(err.message || 'Error inesperado al resolver.');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setError(null);
    setResult(null);
  };

  return { solve, reset, loading, error, result };
}
