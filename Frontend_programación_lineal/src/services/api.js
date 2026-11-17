/**
 * Servicio API para comunicarse con el Backend FastAPI
 */

const API_BASE_URL = '/api';

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
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const message =
      errorData.detail?.[0]?.msg ||
      errorData.detail ||
      'Error al procesar el problema en el servidor.';
    throw new Error(message);
  }

  return response.json();
}
