/**
 * Servicio API para comunicarse con el Backend FastAPI
 */

const API_BASE_URL = '/api';

function extractApiError(errorData, fallback) {
  if (Array.isArray(errorData?.detail) && errorData.detail.length > 0) {
    const first = errorData.detail[0];
    const msg = first.msg?.replace(/^Value error,\s*/i, '') || fallback;
    return msg;
  }
  if (typeof errorData?.detail === 'string') {
    return errorData.detail;
  }
  return fallback;
}

export async function checkHealth() {
  const response = await fetch(`${API_BASE_URL}/health`);
  if (!response.ok) {
    throw new Error('Error al conectar con el servidor.');
  }
  return response.json();
}

export async function solveLinearProblem(payload) {
  const response = await fetch(`${API_BASE_URL}/solve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      extractApiError(errorData, 'Error al procesar el problema en el servidor.')
    );
  }

  return response.json();
}

export async function compareLinearMethods(payload) {
  const response = await fetch(`${API_BASE_URL}/compare`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      extractApiError(errorData, 'Error al comparar los métodos en el servidor.')
    );
  }

  return response.json();
}

export async function exportSolutionPdf(payload) {
  const response = await fetch(`${API_BASE_URL}/export/pdf`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      extractApiError(errorData, 'Error al generar el archivo PDF en el servidor.')
    );
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `solucion_pl_${payload.method || 'big_m'}.pdf`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}
