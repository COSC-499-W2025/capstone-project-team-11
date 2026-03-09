import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { API_BASE_URL } from './api';

function PortfolioPage({ onBack }) {
  const [phase, setPhase] = useState('setup');

  // Setup form fields
  const [username, setUsername] = useState('');
  const [legalName, setLegalName] = useState('');
  const [excludedProjectIds, setExcludedProjectIds] = useState([]);

  // Data for form population
  const [allProjects, setAllProjects] = useState([]);
  const [isLoadingProjects, setIsLoadingProjects] = useState(true);
  const [loadError, setLoadError] = useState('');
  const [contributorOptions, setContributorOptions] = useState([]);

  // Validation state
  const [validationError, setValidationError] = useState('');

  useEffect(() => {
    axios
      .get(`${API_BASE_URL}/projects`)
      .then((res) => setAllProjects(Array.isArray(res.data) ? res.data : []))
      .catch((err) => setLoadError(err.message))
      .finally(() => setIsLoadingProjects(false));
  }, []);

  useEffect(() => {
    const loadContributors = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/contributors`);
        const contributors = Array.isArray(response.data) ? response.data : [];
        setContributorOptions(contributors);
      } catch {
        setContributorOptions([]);
      }
    };

    loadContributors();
  }, []);

  const toggleExclude = (id) => {
    setExcludedProjectIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  };

  const handleGenerate = () => {
    if (!username) {
      setValidationError('Please select a username.');
      return;
    }
    const eligible = allProjects.filter(
      (p) => !excludedProjectIds.includes(p.id ?? p.project_id)
    );
    if (eligible.length < 3) {
      setValidationError(
        'You need at least 3 projects to generate a portfolio. Adjust your exclusion list or scan more projects.'
      );
      return;
    }
    setValidationError('');
    setPhase('dashboard');
  };

  const displayName = legalName.trim() || username;

  // Web portfolio dashboard phase 
  if (phase === 'dashboard') {
    return (
      <div className="page-shell portfolio-page">
        <header className="app-header">
          <h1>Web Portfolio</h1>
          <p>Preview — populate with real data in the next step.</p>
        </header>

        <div className="portfolio-toolbar">
          <button type="button" className="secondary" onClick={() => setPhase('setup')}>
            Back to Setup
          </button>
        </div>

        <div className="portfolio-dashboard">
          {/* Header tile */}
          <section className="portfolio-header">
            <p className="portfolio-dashboard-name">{displayName}</p>
            <p className="tile-placeholder-text">Brief summary will appear here.</p>
          </section>

          {/* Two-column tiles: heatmap + timeline */}
          <div className="portfolio-row">
            <section className="portfolio-tile">
              <h3 className="tile-heading">Activity Heatmap</h3>
              <div className="placeholder">
                <p className="tile-placeholder-text">Contribution activity over time will appear here.</p>
              </div>
            </section>
            <section className="portfolio-tile">
              <h3 className="tile-heading">Skills Timeline</h3>
              <div className="placeholder">
                <p className="tile-placeholder-text">Skill progression chart will appear here.</p>
              </div>
            </section>
          </div>

          {/* Featured projects tile */}
          <section className="portfolio-tile">
            <h3 className="tile-heading">Featured Projects</h3>
            <p className="tile-placeholder-text">Your top 3 projects will be showcased here.</p>
            <div className="project-card-container">
              {[1, 2, 3].map((i) => (
                <div key={i} className="project-card">
                  <div className="card-bar" />
                  <div className="card-bar" />
                </div>
              ))}
            </div>
          </section>

          {/* All projects section */}
          <section className="portfolio-tile">
            <div className="all-projects-header">
              <h3 className="tile-heading">All Projects</h3>
              <div className="all-projects-search">
                <input type="text" className="portfolio-input" placeholder="Search projects..." disabled />
                <select className="portfolio-select" disabled>
                  <option>Filter by language</option>
                </select>
              </div>
            </div>
            <p className="tile-placeholder-text">All scanned project cards will appear here.</p>
            <div className="project-card-container">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="project-card">
                  <div className="card-bar" />
                  <div className="card-bar" />
                </div>
              ))}
            </div>
          </section>
        </div>
      </div>
    );
  }

  // Setup phase
  return (
    <div className="page-shell portfolio-page">
      <header className="app-header">
        <h1>Generate Portfolio</h1>
        <p>Build a web portfolio from your scanned projects.</p>
      </header>

      <div className="portfolio-toolbar">
        <button type="button" className="secondary" onClick={onBack}>
          Back to Main Menu
        </button>
      </div>

      <section className="portfolio-setup-panel">
        <h2>Portfolio Setup</h2>

        {isLoadingProjects && <p>Loading projects...</p>}
        {loadError && <p className="portfolio-error">{loadError}</p>}

        {!isLoadingProjects && allProjects.length < 3 && (
          <p className="portfolio-notice">
            You need at least 3 scanned projects to build a portfolio. Go to{' '}
            <strong>Scan Project</strong> first.
          </p>
        )}

        {!isLoadingProjects && allProjects.length >= 3 && (
          <div className="portfolio-form">
            <label className="portfolio-form-label">
              GitHub Username
              <select
                className="portfolio-select"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              >
                <option value="">— select a contributor —</option>
                {contributorOptions.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </label>

            <label className="portfolio-form-label">
              Display Name{' '}
              <span style={{ fontWeight: 400, color: '#5a6a5a' }}>(optional)</span>
              <input
                type="text"
                className="portfolio-input"
                value={legalName}
                onChange={(e) => setLegalName(e.target.value)}
                placeholder="e.g. Alice Johnson"
              />
              <span className="portfolio-hint">
                Shown in the portfolio header instead of your GitHub username.
              </span>
            </label>

            <fieldset className="portfolio-exclusion-fieldset">
              <legend>Included Projects</legend>
              <p className="portfolio-hint">
                Uncheck any projects you do NOT want included in your portfolio.
              </p>
              {allProjects.map((project) => {
                const id = project.id ?? project.project_id;
                return (
                  <label key={id} className="toggle-row">
                    <input
                      type="checkbox"
                      checked={!excludedProjectIds.includes(id)}
                      onChange={() => toggleExclude(id)}
                    />
                    <span>{project.display_name ?? project.name}</span>
                  </label>
                );
              })}
            </fieldset>

            {validationError && (
              <p className="portfolio-error">{validationError}</p>
            )}

            <div className="portfolio-form-actions">
              <button type="button" onClick={handleGenerate}>
                Generate Web Portfolio
              </button>
            </div>
          </div>
        )}
      </section>
    </div>
  );
}

export default PortfolioPage;
