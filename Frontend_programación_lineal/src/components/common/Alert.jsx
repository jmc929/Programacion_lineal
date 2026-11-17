import React from 'react';

export function Alert({ type = 'info', message, children }) {
  return (
    <div className={`alert alert-${type}`}>
      {message && <span>{message}</span>}
      {children}
    </div>
  );
}
