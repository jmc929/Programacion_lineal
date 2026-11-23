/**
 * Utilidades para cargar/guardar problemas (JSON y CSV) y ejemplos de evaluación.
 */
import { validateRationalInput } from './formatters.js';

export const EXAMPLE_PROBLEMS = [
  {
    id: 'eval1',
    name: 'Ej. 1 — Estándar, redundante y gráfico (Z = 3380)',
    variableCount: 2,
    direction: 'max',
    objectiveTerms: [
      { varIndex: 0, coefficient: '50' },
      { varIndex: 1, coefficient: '80' },
    ],
    constraints: [
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
    ],
  },
  {
    id: 'eval2',
    name: 'Ej. 2 — Minimización, =, ≥, RHS negativo (Z = 17/5)',
    variableCount: 2,
    direction: 'min',
    objectiveTerms: [
      { varIndex: 0, coefficient: '4' },
      { varIndex: 1, coefficient: '1' },
    ],
    constraints: [
      {
        terms: [
          { varIndex: 0, coefficient: '3' },
          { varIndex: 1, coefficient: '1' },
        ],
        sense: '=',
        rhs: '3',
      },
      {
        terms: [
          { varIndex: 0, coefficient: '4' },
          { varIndex: 1, coefficient: '3' },
        ],
        sense: '>=',
        rhs: '6',
      },
      {
        terms: [
          { varIndex: 0, coefficient: '-1' },
          { varIndex: 1, coefficient: '-2' },
        ],
        sense: '>=',
        rhs: '-4',
      },
    ],
  },
  {
    id: 'eval3',
    name: 'Ej. 3 — Tres variables (Z = 1350, sin gráfico)',
    variableCount: 3,
    direction: 'max',
    objectiveTerms: [
      { varIndex: 0, coefficient: '3' },
      { varIndex: 1, coefficient: '2' },
      { varIndex: 2, coefficient: '5' },
    ],
    constraints: [
      {
        terms: [
          { varIndex: 0, coefficient: '1' },
          { varIndex: 1, coefficient: '2' },
          { varIndex: 2, coefficient: '1' },
        ],
        sense: '<=',
        rhs: '430',
      },
      {
        terms: [
          { varIndex: 0, coefficient: '3' },
          { varIndex: 2, coefficient: '2' },
        ],
        sense: '<=',
        rhs: '460',
      },
      {
        terms: [
          { varIndex: 0, coefficient: '1' },
          { varIndex: 1, coefficient: '4' },
        ],
        sense: '<=',
        rhs: '420',
      },
    ],
  },
  {
    id: 'eval4',
    name: 'Ej. 4 — Problema infactible',
    variableCount: 2,
    direction: 'max',
    objectiveTerms: [
      { varIndex: 0, coefficient: '1' },
      { varIndex: 1, coefficient: '1' },
    ],
    constraints: [
      {
        terms: [
          { varIndex: 0, coefficient: '1' },
          { varIndex: 1, coefficient: '1' },
        ],
        sense: '<=',
        rhs: '2',
      },
      {
        terms: [
          { varIndex: 0, coefficient: '1' },
          { varIndex: 1, coefficient: '1' },
        ],
        sense: '>=',
        rhs: '5',
      },
    ],
  },
  {
    id: 'eval5',
    name: 'Ej. 5 — Problema no acotado',
    variableCount: 2,
    direction: 'max',
    objectiveTerms: [
      { varIndex: 0, coefficient: '1' },
      { varIndex: 1, coefficient: '1' },
    ],
    constraints: [
      {
        terms: [
          { varIndex: 0, coefficient: '1' },
          { varIndex: 1, coefficient: '-1' },
        ],
        sense: '<=',
        rhs: '1',
      },
      {
        terms: [
          { varIndex: 0, coefficient: '-1' },
          { varIndex: 1, coefficient: '1' },
        ],
        sense: '<=',
        rhs: '2',
      },
    ],
  },
  {
    id: 'eval6',
    name: 'Ej. 6 — Soluciones óptimas múltiples (Z = 10)',
    variableCount: 2,
    direction: 'max',
    objectiveTerms: [
      { varIndex: 0, coefficient: '2' },
      { varIndex: 1, coefficient: '4' },
    ],
    constraints: [
      {
        terms: [
          { varIndex: 0, coefficient: '1' },
          { varIndex: 1, coefficient: '2' },
        ],
        sense: '<=',
        rhs: '5',
      },
      {
        terms: [
          { varIndex: 0, coefficient: '1' },
          { varIndex: 1, coefficient: '1' },
        ],
        sense: '<=',
        rhs: '4',
      },
    ],
  },
  {
    id: 'eval7',
    name: 'Ej. 7 — Solución degenerada (Z = 18)',
    variableCount: 2,
    direction: 'max',
    objectiveTerms: [
      { varIndex: 0, coefficient: '3' },
      { varIndex: 1, coefficient: '9' },
    ],
    constraints: [
      {
        terms: [
          { varIndex: 0, coefficient: '1' },
          { varIndex: 1, coefficient: '4' },
        ],
        sense: '<=',
        rhs: '8',
      },
      {
        terms: [
          { varIndex: 0, coefficient: '1' },
          { varIndex: 1, coefficient: '2' },
        ],
        sense: '<=',
        rhs: '4',
      },
    ],
  },
];

function termsToDenseVector(terms, variableCount) {
  const vec = Array(variableCount).fill('0');
  for (const t of terms) {
    if (t.varIndex >= 0 && t.varIndex < variableCount) {
      vec[t.varIndex] = String(t.coefficient).trim();
    }
  }
  return vec;
}

function denseVectorToTerms(vec) {
  const terms = [];
  vec.forEach((coeff, idx) => {
    const s = String(coeff).trim();
    if (s !== '0' && s !== '+0' && s !== '-0') {
      terms.push({ varIndex: idx, coefficient: s });
    }
  });
  return terms.length > 0 ? terms : [{ varIndex: 0, coefficient: '0' }];
}

function triggerDownload(content, filename, mimeType) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

export function exportProblemToJson({ variableCount, direction, method, objectiveTerms, constraints }) {
  const payload = {
    direction,
    method: method === 'compare' ? 'big_m' : method,
    objective: termsToDenseVector(objectiveTerms, variableCount),
    constraints: constraints.map((c) => ({
      coefficients: termsToDenseVector(c.terms, variableCount),
      sense: c.sense,
      rhs: String(c.rhs).trim(),
    })),
  };
  triggerDownload(
    JSON.stringify(payload, null, 2),
    'problema_pl.json',
    'application/json;charset=utf-8'
  );
}

export function exportProblemToCsv({ variableCount, direction, objectiveTerms, constraints }) {
  const varHeaders = Array.from({ length: variableCount }, (_, i) => `x${i + 1}`);
  const rows = [
    ['type', ...varHeaders, 'sense', 'rhs'].join(','),
    [direction, ...termsToDenseVector(objectiveTerms, variableCount), '', ''].join(','),
    ...constraints.map((c, idx) =>
      [`R${idx + 1}`, ...termsToDenseVector(c.terms, variableCount), c.sense, String(c.rhs).trim()].join(',')
    ),
  ];
  triggerDownload(rows.join('\n'), 'problema_pl.csv', 'text/csv;charset=utf-8');
}

function validateAndNormalizeImported(obj) {
  if (!obj || typeof obj !== 'object') {
    throw new Error('El archivo no contiene un problema válido.');
  }
  const direction = String(obj.direction || 'max').toLowerCase();
  if (direction !== 'max' && direction !== 'min') {
    throw new Error('La dirección debe ser "max" o "min".');
  }
  if (!Array.isArray(obj.objective) || obj.objective.length < 1) {
    throw new Error('La función objetivo debe tener al menos un coeficiente.');
  }
  const variableCount = obj.objective.length;
  obj.objective.forEach((val, idx) => {
    const check = validateRationalInput(val);
    if (!check.valid) {
      throw new Error(`Función objetivo (x${idx + 1}): ${check.error}`);
    }
  });

  const rawConstraints = Array.isArray(obj.constraints) ? obj.constraints : [];
  const constraints = rawConstraints.map((c, rIdx) => {
    if (!Array.isArray(c.coefficients) || c.coefficients.length !== variableCount) {
      throw new Error(
        `Restricción R${rIdx + 1}: se esperaban ${variableCount} coeficientes.`
      );
    }
    c.coefficients.forEach((val, cIdx) => {
      const check = validateRationalInput(val);
      if (!check.valid) {
        throw new Error(`Restricción R${rIdx + 1} (x${cIdx + 1}): ${check.error}`);
      }
    });
    if (!['<=', '>=', '='].includes(c.sense)) {
      throw new Error(`Restricción R${rIdx + 1}: sentido inválido ("${c.sense}"). Usa <=, >= o =.`);
    }
    const rhsCheck = validateRationalInput(c.rhs);
    if (!rhsCheck.valid) {
      throw new Error(`Restricción R${rIdx + 1} (RHS): ${rhsCheck.error}`);
    }
    return {
      terms: denseVectorToTerms(c.coefficients),
      sense: c.sense,
      rhs: String(c.rhs).trim(),
    };
  });

  const method = ['big_m', 'revised_simplex'].includes(obj.method)
    ? obj.method
    : undefined;

  return {
    variableCount,
    direction,
    method,
    objectiveTerms: denseVectorToTerms(obj.objective),
    constraints,
  };
}

export function parseProblemFile(filename, content) {
  const lower = filename.toLowerCase();
  const trimmed = content.trim();
  if (!trimmed) {
    throw new Error('El archivo seleccionado está vacío.');
  }

  if (lower.endsWith('.json') || trimmed.startsWith('{')) {
    let parsed;
    try {
      parsed = JSON.parse(trimmed);
    } catch {
      throw new Error('El archivo JSON tiene un formato sintáctico inválido.');
    }
    return validateAndNormalizeImported(parsed);
  }

  if (lower.endsWith('.csv') || trimmed.includes(',')) {
    const lines = trimmed
      .split(/\r?\n/)
      .map((l) => l.trim())
      .filter((l) => l.length > 0);
    if (lines.length < 2) {
      throw new Error('El archivo CSV debe contener al menos encabezado y función objetivo.');
    }

    const header = lines[0].split(',').map((s) => s.trim().toLowerCase());
    const hasHeader = header[0] === 'type' || header[0] === 'tipo';
    const dataLines = hasHeader ? lines.slice(1) : lines;

    const objCols = dataLines[0].split(',').map((s) => s.trim());
    const dir = objCols[0].toLowerCase();
    if (dir !== 'max' && dir !== 'min') {
      throw new Error(
        'La primera fila de datos del CSV debe iniciar con "max" o "min" seguida de los coeficientes de Z.'
      );
    }

    // Determine variableCount from header or constraint rows
    let variableCount;
    if (hasHeader && header.includes('sense')) {
      variableCount = header.indexOf('sense') - 1;
    } else if (dataLines.length >= 2) {
      variableCount = dataLines[1].split(',').length - 3;
    } else {
      variableCount = objCols.slice(1).filter((v) => v !== '').length;
    }

    if (variableCount < 1) {
      throw new Error('No se detectaron columnas de variables en el archivo CSV.');
    }

    const objective = objCols.slice(1, 1 + variableCount);
    const constraints = dataLines.slice(1).map((line, idx) => {
      const cols = line.split(',').map((s) => s.trim());
      if (cols.length < variableCount + 3) {
        throw new Error(`Fila de restricción ${idx + 1} incompleta en el CSV.`);
      }
      return {
        coefficients: cols.slice(1, 1 + variableCount),
        sense: cols[1 + variableCount],
        rhs: cols[2 + variableCount],
      };
    });

    return validateAndNormalizeImported({
      direction: dir,
      objective,
      constraints,
    });
  }

  throw new Error('Formato no soportado. Usa un archivo .json o .csv.');
}
