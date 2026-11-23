/**
 * Utilidades para validación y formateo de fracciones y costos Big M
 */

export function parseFractionToFloat(val) {
  if (val === null || val === undefined || val === '') return null;
  const s = String(val).trim();
  if (s.includes('/')) {
    const [num, den] = s.split('/').map(Number);
    if (!Number.isFinite(num) || !Number.isFinite(den) || den === 0) return null;
    return num / den;
  }
  const n = Number(s);
  return Number.isFinite(n) ? n : null;
}

export function formatFraction(val, showDecimal = false) {
  if (val === null || val === undefined) return '';
  const str = String(val);
  if (!showDecimal || !str.includes('/')) return str;
  const approx = parseFractionToFloat(str);
  if (approx === null) return str;
  const dec = Number(approx.toFixed(4)).toString();
  return `${str} (${dec})`;
}

export function formatBound(val, isLower = false, showDecimal = false) {
  if (val === null || val === undefined) {
    return isLower ? '-∞' : '+∞';
  }
  return formatFraction(val, showDecimal);
}

export function formatDelta(val, showDecimal = false) {
  if (val === null || val === undefined) {
    return '∞';
  }
  return formatFraction(val, showDecimal);
}

export function formatBigMCost(cost, showDecimal = false) {
  if (cost === null || cost === undefined) return '0';
  if (typeof cost !== 'object' || !('m_coefficient' in cost)) {
    return formatFraction(cost, showDecimal);
  }
  const m = String(cost.m_coefficient);
  const c = String(cost.constant);
  if (m === '0') return formatFraction(c, showDecimal);

  let mPart;
  if (m === '1') mPart = 'M';
  else if (m === '-1') mPart = '-M';
  else mPart = `${formatFraction(m, false)}M`;

  if (c === '0') return mPart;
  if (c.startsWith('-')) {
    return `${mPart} - ${formatFraction(c.slice(1), false)}`;
  }
  return `${mPart} + ${formatFraction(c, false)}`;
}

export function validateRationalInput(str) {
  if (str === null || str === undefined) {
    return { valid: false, error: 'Campo vacío' };
  }
  const trimmed = String(str).trim();
  if (trimmed === '') {
    return { valid: false, error: 'Campo vacío' };
  }

  // Fracción a/b (permitiendo signo al inicio)
  const fractionMatch = trimmed.match(/^[+-]?\d+\/([+-]?\d+)$/);
  if (fractionMatch) {
    const den = parseInt(fractionMatch[1], 10);
    if (den === 0) {
      return { valid: false, error: 'División por cero no permitida' };
    }
    return { valid: true, error: null };
  }

  // Entero o decimal (ej: -3, +2.5, .5, 0.25)
  const numberRegex = /^[+-]?(\d+(\.\d+)?|\.\d+)$/;
  if (numberRegex.test(trimmed)) {
    return { valid: true, error: null };
  }

  return {
    valid: false,
    error: `Valor inválido ("${trimmed}"). Usa enteros, decimales (0.5) o fracciones (1/3).`,
  };
}

export function isValidRationalInput(str) {
  return validateRationalInput(str).valid;
}
