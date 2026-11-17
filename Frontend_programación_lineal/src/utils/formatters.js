/**
 * Utilidades para formateo de fracciones y números racionales
 */

export function formatFraction(val) {
  if (val === null || val === undefined) return '';
  return String(val);
}

export function isValidRationalInput(str) {
  if (typeof str !== 'string' && typeof str !== 'number') return false;
  const trimmed = String(str).trim();
  // Entero o fracción simple "a/b" o decimal "a.b"
  const fractionRegex = /^-?\d+(\/\d+)?$/;
  const decimalRegex = /^-?\d+(\.\d+)?$/;
  return fractionRegex.test(trimmed) || decimalRegex.test(trimmed);
}
