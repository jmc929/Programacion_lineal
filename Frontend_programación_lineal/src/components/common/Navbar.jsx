import React from 'react';

export function Navbar({ activePage, onNavigate }) {
  return (
    <header className="navbar">
      <div className="navbar-brand" onClick={() => onNavigate('home')} style={{ cursor: 'pointer' }}>
        <h2>📐 Simplex Solver</h2>
      </div>
      <nav className="navbar-nav">
        <button
          className={`nav-link ${activePage === 'home' ? 'active' : ''}`}
          onClick={() => onNavigate('home')}
        >
          Inicio
        </button>
        <button
          className={`nav-link ${activePage === 'solver' ? 'active' : ''}`}
          onClick={() => onNavigate('solver')}
        >
          Solucionador
        </button>
        <button
          className={`nav-link ${activePage === 'about' ? 'active' : ''}`}
          onClick={() => onNavigate('about')}
        >
          Acerca de
        </button>
      </nav>
    </header>
  );
}
