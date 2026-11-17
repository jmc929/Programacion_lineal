import React, { useState } from 'react';
import { Navbar, Footer } from './components/common';
import { HomePage, SolverPage, AboutPage, NotFoundPage } from './pages';
import './App.css';

export function App() {
  const [currentPage, setCurrentPage] = useState('home');

  const renderPage = () => {
    switch (currentPage) {
      case 'home':
        return <HomePage onNavigate={setCurrentPage} />;
      case 'solver':
        return <SolverPage />;
      case 'about':
        return <AboutPage />;
      default:
        return <NotFoundPage onNavigateHome={() => setCurrentPage('home')} />;
    }
  };

  return (
    <div className="app-layout">
      <Navbar activePage={currentPage} onNavigate={setCurrentPage} />
      <main className="main-content">{renderPage()}</main>
      <Footer />
    </div>
  );
}

export default App;
