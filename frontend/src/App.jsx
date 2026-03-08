import React, { useEffect, useState } from 'react';
import axios from 'axios';
import ScanPage from './ScanPage.jsx';
import RankProjectsPage from './RankProjectsPage.jsx';
import ScannedProjectsPage from './ScannedProjectsPage.jsx';
import PortfolioPage from './PortfolioPage.jsx';
import { API_BASE_URL } from './api';


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

const getPageFromHash = () => {
  if (window.location.hash === '#/main-menu') {
    return 'main-menu';
  }
  if (window.location.hash === '#/scan') {
    return 'scan';
  }
  if (window.location.hash === '#/rank-projects') {
    return 'rank-projects';
  if (window.location.hash === '#/projects') {
    return 'projects';
  }
  if (window.location.hash === '#/portfolio') {
    return 'portfolio';
  }
  return 'home';
};

function App() {
  const [status, setStatus] = useState('Not tested');
  const [isLoading, setIsLoading] = useState(false);
  const [page, setPage] = useState(getPageFromHash());
  const [activeMenuItem, setActiveMenuItem] = useState(null);
  const [toasts, setToasts] = useState([]);

  useEffect(() => {
    const onHashChange = () => {
      setPage(getPageFromHash());
    };

    window.addEventListener('hashchange', onHashChange);
    return () => window.removeEventListener('hashchange', onHashChange);
  }, []);

  const navigateTo = (target) => {
    if (target === 'main-menu') {
      window.location.hash = '/main-menu';
      return;
    }
    if (target === 'scan') {
      window.location.hash = '/scan';
      return;
    }
    if (target === 'rank-projects') {
      window.location.hash = '/rank-projects';
    if (target === 'projects') {
      window.location.hash = '/projects';
      return;
    }
    if (target === 'portfolio') {
      window.location.hash = '/portfolio';
      return;
    }
    window.location.hash = '';
  };

  const addToast = (message) => {
    const id = `${Date.now()}-${Math.random()}`;
    setToasts((prev) => [...prev, { id, message }]);

    window.setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 2500);
  };

  const handleMenuClick = (title) => {
    setActiveMenuItem(title);

    if (title === 'Scan Project') {
      navigateTo('scan');
      return;
    }
    if (title === 'Rank Projects') {
      navigateTo('rank-projects');
      return;
    }

    if (title === 'View/Manage Scanned Projects') {
      navigateTo('projects');
      return;
    }

    if (title === 'Generate Portfolio') {
      navigateTo('portfolio');
      return;
    }

    addToast(`${title} clicked (coming soon)`);
  };

  const testConnection = async () => {
    setIsLoading(true);
    setStatus('Not tested');

    try {
      await axios.get(`${API_BASE_URL}/projects`);
      setStatus('Connected to backend!');
    } catch (err) {
      setStatus(`Failed: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  if (page === 'scan') {
    return <ScanPage onBack={() => navigateTo('main-menu')} />;
  }

  if (page === 'rank-projects') {
    return <RankProjectsPage onBack={() => navigateTo('main-menu')} />;
  if (page === 'projects') {
    return <ScannedProjectsPage onBack={() => navigateTo('main-menu')} />;
  }

  if (page === 'portfolio') {
    return <PortfolioPage onBack={() => navigateTo('main-menu')} />;
  }

  if (page === 'main-menu') {
    return (
      <div className="page-shell main-menu-page">
        <div className="toast-stack" aria-live="polite" aria-atomic="true">
          {toasts.map((t) => (
            <div key={t.id} className="toast" role="status">
              {t.message}
            </div>
          ))}
        </div>

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
                <button
                  key={item.title}
                  type="button"
                  className={`menu-action-button ${
                    activeMenuItem === item.title ? 'is-active' : ''
                  }`}
                  onClick={() => handleMenuClick(item.title)}
                >
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
                Start with <strong>Scan Project</strong> to import a project folder or zip. Once
                scanned, you can generate resumes/portfolios and run ranking or summary tools.
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