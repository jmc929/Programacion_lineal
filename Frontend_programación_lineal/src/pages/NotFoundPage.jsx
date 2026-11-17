import React from 'react';
import { Button } from '../components/common';

export function NotFoundPage({ onNavigateHome }) {
  return (
    <div className="page-container not-found-page">
      <h2>404 - Página no encontrada</h2>
      <p>La página solicitada no existe.</p>
      <Button variant="primary" onClick={onNavigateHome}>
        Volver al Solucionador
      </Button>
    </div>
  );
}
