import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import ScanPage from './ScanPage.jsx';
import ResumePage from './ResumePage.jsx';
import RankProjectsPage from './RankProjectsPage.jsx';
import ScannedProjectsPage from './ScannedProjectsPage.jsx';
import DatabaseMaintenance from './DatabaseMaintenance.jsx';
import PortfolioPage from './PortfolioPage.jsx';
import ConsentPage from './ConsentPage.jsx';
import { API_BASE_URL } from './api';

const MENU_ITEMS = [
  {
    title: 'Scan Project',
    detail: 'Import a local folder or zip and index commits, files, and contributors.',
    icon: '⬡',
    accent: '#4ade80',
  },
  {
    title: 'View/Manage Scanned Projects',
    detail: 'Browse existing scans, update display names, or clean up old entries.',
    icon: '◈',
    accent: '#60a5fa',
  },
  {
    title: 'Generate Resume',
    detail: 'Build a contributor-focused resume using detected evidence and project data.',
    icon: '◎',
    accent: '#f472b6',
  },
  {
    title: 'Generate Portfolio',
    detail: 'Create a project portfolio summary with key impact highlights.',
    icon: '◉',
    accent: '#fb923c',
  },
  {
    title: 'Rank Projects',
    detail: 'Sort by importance and compare contribution strength across projects.',
    icon: '◆',
    accent: '#a78bfa',
  },
  {
    title: 'Manage Database',
    detail: 'Inspect stored data, remove projects, or clear database contents.',
    icon: '⬢',
    accent: '#fbbf24',
  },
];

const getPageFromHash = () => {
  const map = {
    '#/main-menu': 'main-menu',
    '#/scan': 'scan',
    '#/resume': 'resume',
    '#/rank-projects': 'rank-projects',
    '#/projects': 'projects',
    '#/database': 'database',
    '#/portfolio': 'portfolio',
  };
  return map[window.location.hash] || 'main-menu';
};

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.07, delayChildren: 0.1 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.25, 0.46, 0.45, 0.94] } },
};


function MenuCard({ item, isActive, onClick }) {
  return (
    <motion.button
      variants={itemVariants}
      whileHover={{ x: 4, transition: { duration: 0.15 } }}
      whileTap={{ scale: 0.98 }}
      onClick={() => onClick(item.title)}
      style={{
        width: '100%',
        margin: 0,
        padding: '0.85rem 1rem',
        background: isActive
          ? 'rgba(255,255,255,0.08)'
          : 'rgba(255,255,255,0.03)',
        border: isActive
          ? `1px solid ${item.accent}55`
          : '1px solid rgba(255,255,255,0.07)',
        borderRadius: '10px',
        cursor: 'pointer',
        textAlign: 'left',
        display: 'flex',
        alignItems: 'flex-start',
        gap: '0.75rem',
        transition: 'background 0.2s ease, border-color 0.2s ease',
        boxShadow: isActive ? `0 0 0 1px ${item.accent}33, 0 4px 16px rgba(0,0,0,0.3)` : 'none',
      }}
    >
      <span
        style={{
          fontSize: '1.1rem',
          lineHeight: 1,
          color: item.accent,
          marginTop: '0.1rem',
          flexShrink: 0,
        }}
      >
        {item.icon}
      </span>
      <span style={{ display: 'flex', flexDirection: 'column', gap: '0.2rem' }}>
        <span
          style={{
            display: 'block',
            fontWeight: 600,
            fontSize: '0.88rem',
            color: '#f1f5f9',
            letterSpacing: '0.01em',
          }}
        >
          {item.title}
        </span>
        <span
          style={{
            display: 'block',
            fontSize: '0.78rem',
            color: 'rgba(241,245,249,0.45)',
            lineHeight: 1.4,
          }}
        >
          {item.detail}
        </span>
      </span>
    </motion.button>
  );
}

function StatCard({ label, value, note }) {
  return (
    <motion.article
      variants={itemVariants}
      style={{
        background: 'rgba(255,255,255,0.04)',
        border: '1px solid rgba(255,255,255,0.08)',
        borderRadius: '12px',
        padding: '1.1rem 1.2rem',
        textAlign: 'left',
      }}
    >
      <p
        style={{
          margin: '0 0 0.3rem',
          fontSize: '0.75rem',
          fontWeight: 600,
          letterSpacing: '0.08em',
          textTransform: 'uppercase',
          color: 'rgba(241,245,249,0.45)',
        }}
      >
        {label}
      </p>
      <p
        style={{
          margin: '0 0 0.3rem',
          fontSize: '1.8rem',
          fontWeight: 700,
          color: '#f1f5f9',
          lineHeight: 1,
        }}
      >
        {value}
      </p>
      <p style={{ margin: 0, fontSize: '0.78rem', color: 'rgba(241,245,249,0.4)', lineHeight: 1.4 }}>
        {note}
      </p>
    </motion.article>
  );
}

function InfoPanel({ title, children }) {
  return (
    <motion.article
      variants={itemVariants}
      style={{
        background: 'rgba(255,255,255,0.04)',
        border: '1px solid rgba(255,255,255,0.07)',
        borderRadius: '12px',
        padding: '1.1rem 1.2rem',
        textAlign: 'left',
      }}
    >
      <h2
        style={{
          margin: '0 0 0.6rem',
          fontSize: '0.8rem',
          fontWeight: 700,
          letterSpacing: '0.1em',
          textTransform: 'uppercase',
          color: 'rgba(241,245,249,0.5)',
        }}
      >
        {title}
      </h2>
      {children}
    </motion.article>
  );
}

function App() {
  const [connStatus, setConnStatus] = useState('idle'); // 'idle' | 'checking' | 'ok' | 'fail'
  const [page, setPage] = useState(getPageFromHash());
  const [activeMenuItem, setActiveMenuItem] = useState(null);
  const [toasts, setToasts] = useState([]);
  const [consentChecked, setConsentChecked] = useState(false);
  const [consentGranted, setConsentGranted] = useState(false);
  const [initialConsent, setInitialConsent] = useState({});

  // Fetch consent status
  useEffect(() => {
    fetch(`${API_BASE_URL}/config`)
      .then((r) => r.ok ? r.json() : Promise.reject())
      .then((cfg) => {
        setInitialConsent(cfg);
        setConsentGranted(Boolean(cfg.data_consent));
      })
      .catch(() => {
        // Backend unreachable, show consent screen anyway
        setConsentGranted(false);
      })
      .finally(() => setConsentChecked(true));
  }, []);

  useEffect(() => {
    const onHashChange = () => setPage(getPageFromHash());
    window.addEventListener('hashchange', onHashChange);
    return () => window.removeEventListener('hashchange', onHashChange);
  }, []);

  const navigateTo = (target) => {
    const routes = {
      'main-menu': '#/main-menu',
      scan: '#/scan',
      resume: '#/resume',
      'rank-projects': '#/rank-projects',
      projects: '#/projects',
      database: '#/database',
      portfolio: '#/portfolio',
    };
    window.location.hash = routes[target] || '';
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
    const routes = {
      'Scan Project': 'scan',
      'Generate Resume': 'resume',
      'Rank Projects': 'rank-projects',
      'View/Manage Scanned Projects': 'projects',
      'Manage Database': 'database',
      'Generate Portfolio': 'portfolio',
    };
    if (routes[title]) {
      navigateTo(routes[title]);
    } else {
      addToast(`${title} — coming soon`);
    }
  };

  const testConnection = async () => {
    setConnStatus('checking');
    try {
      await axios.get(`${API_BASE_URL}/projects`);
      setConnStatus('ok');
    } catch {
      setConnStatus('fail');
    }
  };

  // Block access to the entire app until we know consent status
  if (!consentChecked) return null;

  // Show consent screen if data consent has not been granted
  if (!consentGranted) {
    return (
      <ConsentPage
        initialConsent={initialConsent}
        onConsented={(result) => {
          const normalized = {
            data_consent: result.dataConsent,
            llm_summary_consent: result.llmSummaryConsent,
            llm_resume_consent: result.llmResumeConsent,
          };
          setInitialConsent(normalized);
          setConsentGranted(result.dataConsent);
          if (result.dataConsent) navigateTo('main-menu');
        }}
      />
    );
  }

  // Sub-pages — pass through unchanged
  if (page === 'scan') return <ScanPage onBack={() => navigateTo('main-menu')} />;
  if (page === 'resume') return <ResumePage onBack={() => navigateTo('main-menu')} />;
  if (page === 'rank-projects') return <RankProjectsPage onBack={() => navigateTo('main-menu')} />;
  if (page === 'projects') return <ScannedProjectsPage onBack={() => navigateTo('main-menu')} />;
  if (page === 'database') return <DatabaseMaintenance onBack={() => navigateTo('main-menu')} />;
  if (page === 'portfolio') return <PortfolioPage onBack={() => navigateTo('main-menu')} />;

  // ── Main Menu ────────────────────────────────────────────────────────────
  if (page === 'main-menu') {
    return (
      <div
        style={{
          minHeight: '100vh',
          fontFamily: "'DM Sans', 'Inter', sans-serif",
        }}
      >
        {/* Toast stack */}
        <div
          style={{
            position: 'fixed',
            top: '1rem',
            right: '1rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '0.5rem',
            zIndex: 9999,
          }}
        >
          <AnimatePresence>
            {toasts.map((t) => (
              <motion.div
                key={t.id}
                initial={{ opacity: 0, x: 40, scale: 0.95 }}
                animate={{ opacity: 1, x: 0, scale: 1 }}
                exit={{ opacity: 0, x: 40, scale: 0.95 }}
                style={{
                  background: 'rgba(15,23,42,0.92)',
                  backdropFilter: 'blur(12px)',
                  border: '1px solid rgba(255,255,255,0.12)',
                  borderRadius: '10px',
                  padding: '0.65rem 1rem',
                  color: '#f1f5f9',
                  fontSize: '0.85rem',
                  boxShadow: '0 10px 30px rgba(0,0,0,0.4)',
                  maxWidth: '280px',
                }}
                role="status"
              >
                {t.message}
              </motion.div>
            ))}
          </AnimatePresence>
        </div>

        <div style={{ maxWidth: '76rem', margin: '0 auto', padding: '0 1rem' }}>
          {/* Header */}
          <motion.header
            initial={{ opacity: 0, y: -16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, ease: [0.25, 0.46, 0.45, 0.94] }}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '1.25rem 1.5rem',
              marginBottom: '1.25rem',
              background: 'rgba(255,255,255,0.04)',
              backdropFilter: 'blur(8px)',
              border: '1px solid rgba(255,255,255,0.08)',
              borderRadius: '14px',
            }}
          >
            <div>
              <h1
                style={{
                  margin: 0,
                  fontSize: '1.15rem',
                  fontWeight: 700,
                  color: '#f1f5f9',
                  letterSpacing: '-0.02em',
                }}
              >
                Capstone MDA
              </h1>
              <p
                style={{
                  margin: '0.15rem 0 0',
                  fontSize: '0.8rem',
                  color: 'rgba(241,245,249,0.45)',
                }}
              >
                Project analysis & portfolio generation toolkit
              </p>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={testConnection}
                disabled={connStatus === 'checking'}
                style={{
                  padding: '0.4rem 0.75rem',
                  background: 'rgba(255,255,255,0.05)',
                  border: connStatus === 'fail'
                    ? '1px solid rgba(248,113,113,0.4)'
                    : '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '8px',
                  color: connStatus === 'fail' ? '#f87171' : 'rgba(241,245,249,0.5)',
                  fontSize: '0.75rem',
                  cursor: connStatus === 'checking' ? 'not-allowed' : 'pointer',
                  boxShadow: 'none',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.35rem',
                }}
              >
                {connStatus === 'checking' ? 'Checking…' : 'Check Connection'}
                {connStatus === 'ok' && (
                  <span style={{ color: '#4ade80', fontSize: '0.85rem', lineHeight: 1 }}>✓</span>
                )}
                {connStatus === 'fail' && (
                  <span style={{ color: '#f87171', fontSize: '0.85rem', lineHeight: 1 }}>✗</span>
                )}
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setConsentGranted(false)}
                style={{
                  padding: '0.4rem 0.75rem',
                  background: 'rgba(255,255,255,0.05)',
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '8px',
                  color: 'rgba(241,245,249,0.5)',
                  fontSize: '0.75rem',
                  cursor: 'pointer',
                  boxShadow: 'none',
                }}
              >
                Privacy Settings
              </motion.button>
              <div
                style={{
                  width: '36px',
                  height: '36px',
                  borderRadius: '10px',
                  background: 'linear-gradient(135deg, #4ade80, #22d3ee)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '1.1rem',
                  fontWeight: 700,
                  color: '#0f172a',
                }}
              >
                M
              </div>
            </div>
          </motion.header>

          {/* Main layout */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: '20rem 1fr',
              gap: '1.25rem',
              alignItems: 'start',
            }}
          >
            {/* Sidebar */}
            <motion.aside
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.45, ease: [0.25, 0.46, 0.45, 0.94] }}
              style={{
                background: 'rgba(255,255,255,0.03)',
                border: '1px solid rgba(255,255,255,0.08)',
                borderRadius: '14px',
                padding: '1.1rem',
              }}
            >
              <p
                style={{
                  margin: '0 0 0.25rem',
                  fontSize: '0.7rem',
                  fontWeight: 700,
                  letterSpacing: '0.1em',
                  textTransform: 'uppercase',
                  color: 'rgba(241,245,249,0.35)',
                  paddingLeft: '0.25rem',
                }}
              >
                Navigation
              </p>
              <p
                style={{
                  margin: '0 0 1rem',
                  fontSize: '0.78rem',
                  color: 'rgba(241,245,249,0.4)',
                  paddingLeft: '0.25rem',
                }}
              >
                Choose an action to get started
              </p>

              <motion.div
                variants={containerVariants}
                initial="hidden"
                animate="visible"
                style={{ display: 'flex', flexDirection: 'column', gap: '0.45rem', marginBottom: '1rem' }}
              >
                {MENU_ITEMS.map((item) => (
                  <MenuCard
                    key={item.title}
                    item={item}
                    isActive={activeMenuItem === item.title}
                    onClick={handleMenuClick}
                  />
                ))}
              </motion.div>

            </motion.aside>

            {/* Content area */}
            <motion.section
              variants={containerVariants}
              initial="hidden"
              animate="visible"
              style={{ display: 'grid', gap: '1rem' }}
            >
              {/* Stats row */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.9rem' }}>
                <StatCard label="Scanned Projects" value="--" note="Run your first scan to populate." />
                <StatCard label="Contributors" value="--" note="Detected from commit history." />
                <StatCard label="Generated Outputs" value="--" note="Resumes, portfolios & summaries." />
              </div>

              <InfoPanel title="Quick Start">
                <p style={{ margin: 0, fontSize: '0.88rem', color: 'rgba(241,245,249,0.65)', lineHeight: 1.6 }}>
                  Start with <strong style={{ color: '#4ade80' }}>Scan Project</strong> to import a
                  folder or zip. Once scanned, generate resumes and portfolios, run ranking or summary
                  tools, and explore contributor insights.
                </p>
              </InfoPanel>

              <InfoPanel title="About">
                <p style={{ margin: 0, fontSize: '0.88rem', color: 'rgba(241,245,249,0.65)', lineHeight: 1.6 }}>
                  This desktop app analyzes code repositories and transforms data into
                  contributor-focused outputs — rankings, summaries, resumes, and portfolios.
                </p>
              </InfoPanel>

              <InfoPanel title="Suggested First Steps">
                <ol
                  style={{
                    margin: 0,
                    padding: '0 0 0 1.2rem',
                    fontSize: '0.88rem',
                    color: 'rgba(241,245,249,0.65)',
                    lineHeight: 2,
                  }}
                >
                  <li>Scan a project.</li>
                  <li>Review scanned projects.</li>
                  <li>Generate a resume or portfolio.</li>
                </ol>
              </InfoPanel>
            </motion.section>
          </div>
        </div>
      </div>
    );
  }

  return null;
}

export default App;
