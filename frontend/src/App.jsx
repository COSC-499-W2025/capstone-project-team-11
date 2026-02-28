import React, { useEffect, useState } from 'react';
import axios from 'axios';

const MENU_ITEMS = [
  {
    title: 'Scan Project',
    detail: 'Import a local folder or zip and index commits, files, and contributors.',
  },
  {
    title: 'View/Manage Scanned Projects',
    detail: 'Browse existing scans, update display names, or clean up old entries.',
  },
  {
    title: 'Generate Resume',
    detail: 'Build a contributor-focused resume using detected evidence and project data.',
  },
  {
    title: 'Generate Portfolio',
    detail: 'Create a project portfolio summary with key impact highlights.',
  },
  {
    title: 'Rank Projects',
    detail: 'Sort by importance and compare contribution strength across projects.',
  },
  {
    title: 'Summarize Contributor Projects',
    detail: 'Generate short summaries for a selected contributor’s strongest projects.',
  },
];

function App() {
  const [status, setStatus] = useState('Not tested');
  const [isLoading, setIsLoading] = useState(false);
  const [page, setPage] = useState(window.location.hash === '#/main-menu' ? 'main-menu' : 'home');

  useEffect(() => {
    const onHashChange = () => {
      setPage(window.location.hash === '#/main-menu' ? 'main-menu' : 'home');
    };

    window.addEventListener('hashchange', onHashChange);
    return () => window.removeEventListener('hashchange', onHashChange);
  }, []);

  const navigateTo = (target) => {
    if (target === 'main-menu') {
      window.location.hash = '/main-menu';
      return;
    }
    window.location.hash = '';
  };

  const testConnection = async () => {
    setIsLoading(true);
    setStatus('Not tested');

    try {
      await axios.get('http://localhost:8000/projects');
      setStatus('Connected to backend!');
    } catch (err) {
      setStatus(`Failed: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  if (page === 'main-menu') {
    return (
      <div className="page-shell main-menu-page">
        <header className="app-header">
          <h1>Capstone MDA Dashboard</h1>
          <p>Project analysis and portfolio generation toolkit</p>
        </header>

        <div className="main-menu-layout">
          <aside className="menu-sidebar">
            <h2>Main Menu</h2>
            <p className="subtitle">Choose an action</p>
            <div className="menu-grid">
              {MENU_ITEMS.map((item) => (
                <button key={item.title} type="button" className="menu-action-button">
                  <span className="menu-action-title">{item.title}</span>
                  <span className="menu-action-detail">{item.detail}</span>
                </button>
              ))}
            </div>
            <button type="button" className="secondary" onClick={() => navigateTo('home')}>
              Back to Connection Test
            </button>
          </aside>

          <section className="menu-content">
            <div className="overview-cards">
              <article className="overview-card">
                <h3>Scanned Projects</h3>
                <p className="overview-value">--</p>
                <p>Appears after you run your first project scan.</p>
              </article>
              <article className="overview-card">
                <h3>Contributors</h3>
                <p className="overview-value">--</p>
                <p>Detected from commit history and linked to project evidence.</p>
              </article>
              <article className="overview-card">
                <h3>Generated Outputs</h3>
                <p className="overview-value">--</p>
                <p>Resumes, portfolios, and summaries are tracked here over time.</p>
              </article>
            </div>

            <article className="info-panel">
              <h2>Quick Help</h2>
              <p>
                Start with <strong>Scan Project</strong> to import a project folder or zip.
                Once scanned, you can generate resumes/portfolios and run ranking or summary tools.
              </p>
            </article>

            <article className="info-panel">
              <h2>Project Information</h2>
              <p>
                This desktop app helps analyze code repositories and transform repository data into
                contributor-focused outputs like rankings, summaries, resumes, and portfolios.
              </p>
            </article>

            <article className="info-panel">
              <h2>Suggested First Steps</h2>
              <ol className="help-list">
                <li>Scan a project.</li>
                <li>Review scanned projects.</li>
                <li>Generate a resume or portfolio.</li>
              </ol>
            </article>
          </section>
        </div>
      </div>
    );
  }

  return (
    <div className="page-shell">
      <h1>Capstone MDA App</h1>
      <button type="button" onClick={testConnection} disabled={isLoading}>
        {isLoading ? 'Checking...' : 'Test Backend Connection'}
      </button>
      <p>Status: {status}</p>

      <button type="button" className="secondary" onClick={() => navigateTo('main-menu')}>
        Go to Main Menu
      </button>
    </div>
  );
}

export default App;
