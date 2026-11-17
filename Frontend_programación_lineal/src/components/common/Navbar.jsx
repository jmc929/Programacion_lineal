import React from 'react';

export function Navbar({ activePage, onNavigate }) {
  return (
    <header className="navbar">
      <div
        className="navbar-brand"
        onClick={() => onNavigate('home')}
        style={{ cursor: 'pointer' }}
      >
        <div className="brand-icon">📐</div>
        <span className="brand-title">SimplexFlow</span>
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
