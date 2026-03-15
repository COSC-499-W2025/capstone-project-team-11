import React, { useEffect, useRef, useState } from 'react';
import axios from 'axios';
import { API_BASE_URL } from './api';

const MAX_FEATURED = 3;

function formatRoleConfidence(value) {
  if (typeof value !== 'number' || Number.isNaN(value)) return '0%';
  return `${Math.round(value * 100)}%`;
}

function ProjectModal({ project, detail, username, displayName, onClose }) {
  const name = project.display_name ?? project.name ?? '(unnamed)';
  const projectId = project.id ?? project.project_id;
  const thumbSrc = getThumbnailSrc(projectId, project.thumbnail_path);

  const languages = Array.isArray(detail?.languages) ? detail.languages : [];
  const skills = Array.isArray(detail?.skills) ? detail.skills : [];
  const llmSummary = detail?.llm_summary?.text ?? null;
  const repoUrl = detail?.project?.repo_url ?? null;

  // Filter contributor roles to only the selected portfolio user
  const allRoles = Array.isArray(detail?.contributor_roles?.contributors)
    ? detail.contributor_roles.contributors
    : [];
  const userRole = allRoles.find(
    (c) => c.name?.toLowerCase() === username?.toLowerCase()
  ) ?? null;

  return (
    <div className="modal-overlay" onClick={onClose} role="dialog" aria-modal="true" aria-label={`${name} details`}>
      <div
        className="modal-card"
        style={{ width: '680px', maxWidth: '95vw', maxHeight: '85vh', overflowY: 'auto', background: 'radial-gradient(circle at center, #0a5948, #08271f 80%)', border: '1px solid rgba(74,222,128,0.18)', textAlign: 'left' }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="detail-card-header" style={{ marginBottom: '1rem' }}>
          <div>
            <span className="panel-eyebrow">Project</span>
            <h3 style={{ margin: 0 }}>{name}</h3>
          </div>
          <button type="button" className="hero-action-button" onClick={onClose}>✕ Close</button>
        </div>

        {thumbSrc && (
          <div style={{ position: 'relative', width: '100%', aspectRatio: '16/9', marginBottom: '1rem', overflow: 'hidden', border: 'none'}}>
            <img src={thumbSrc} alt={`${name} thumbnail`} style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'contain', background: 'rgba(255,255,255,0)' }} />
          </div>
        )}

        {llmSummary && (
          <div className="llm-summary-card" style={{ marginBottom: '1rem' }}>
            <span className="panel-eyebrow">About</span>
            <p style={{ margin: '0.25rem 0 0' }}>{llmSummary}</p>
          </div>
        )}

        <div className="detail-grid" style={{ marginBottom: '1rem' }}>
          {languages.length > 0 && (
            <article className="detail-card">
              <div className="detail-card-header">
                <span className="panel-eyebrow">Languages</span>
              </div>
              <div className="chip-cloud">
                {languages.map((lang) => <span key={lang} className="detail-chip">{lang}</span>)}
              </div>
            </article>
          )}
          {skills.length > 0 && (
            <article className="detail-card">
              <div className="detail-card-header">
                <span className="panel-eyebrow">Skills</span>
              </div>
              <div className="chip-cloud">
                {skills.map((skill) => <span key={skill} className="detail-chip">{skill}</span>)}
              </div>
            </article>
          )}
        </div>

        {userRole && (
          <div style={{ marginBottom: '1rem' }}>
            <span className="panel-eyebrow">{displayName}'s Role</span>
            <div className="contributor-role-card" style={{ marginTop: '0.4rem' }}>
              <p className="contributor-role-primary">
                {userRole.primary_role}{userRole.role_description ? ` — ${userRole.role_description}` : ''}
              </p>
              <p className="contributor-role-meta">Confidence: {formatRoleConfidence(userRole.confidence)}</p>
              {Array.isArray(userRole.secondary_roles) && userRole.secondary_roles.length > 0 && (
                <p className="contributor-role-meta">Secondary: {userRole.secondary_roles.join(', ')}</p>
              )}
            </div>
          </div>
        )}

        <div className="modal-actions">
          {repoUrl && (
            <a className="hero-action-button" href={repoUrl} target="_blank" rel="noreferrer">
              Open Repository
            </a>
          )}
          <button type="button" className="hero-action-button" onClick={onClose}>Close</button>
        </div>
      </div>
    </div>
  );
}

function getThumbnailSrc(projectId, thumbnailPath) {
  if (!projectId || !thumbnailPath) return null;
  if (/^https?:\/\//i.test(thumbnailPath) || /^data:/i.test(thumbnailPath)) {
    return thumbnailPath;
  }
  return `${API_BASE_URL}/projects/${projectId}/thumbnail/image?v=${encodeURIComponent(thumbnailPath)}`;
}

function PortfolioPage({ onBack, showStars = true }) {
  const [phase, setPhase] = useState('setup');

  // Setup form fields
  const [username, setUsername] = useState('');
  const [legalName, setLegalName] = useState('');
  const [excludedProjectIds, setExcludedProjectIds] = useState([]);

  // Data for form population
  const [allProjects, setAllProjects] = useState([]);
  const [isLoadingProjects, setIsLoadingProjects] = useState(true);
  const [contributorOptions, setContributorOptions] = useState([]);

  // User-specific project filtering (for "Include Projects" tile)
  const [userProjects, setUserProjects] = useState([]);
  const [isLoadingUserProjects, setIsLoadingUserProjects] = useState(false);
  const [includedProjects, setIncludedProjects] = useState([]);

  // Web portfolio information
  const [portfolioId, setPortfolioId] = useState(null);
  const [portfolioMeta, setPortfolioMeta] = useState(null);
  const [heatmapData, setHeatmapData] = useState({ cells: [], max_value: 0 });
  const [timelineData, setTimelineData] = useState([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [projectSearch, setProjectSearch] = useState('');
  // Map of project id → full /projects/{id} response (fetched at generation time)
  const [projectDetails, setProjectDetails] = useState({});
  const [expandedProjectId, setExpandedProjectId] = useState(null);

  // Universal toast (4 seconds, auto-dismiss, auto-restart, clears on new toast received)
  const [toast, setToast] = useState(null); 
  const toastTimer = useRef(null);

  const showToast = (message, type) => { // type = 'error', 'info', or 'success' 
    clearTimeout(toastTimer.current);
    setToast({ message, type });
    toastTimer.current = setTimeout(() => setToast(null), 4000);
  };

  // Track which projects are starred/featured by storing their names in a set
  const [featuredIds, setFeaturedIds] = useState(new Set());

  useEffect(() => {
    axios
      .get(`${API_BASE_URL}/projects`)
      .then((res) => {
        const raw = Array.isArray(res.data) ? res.data : [];
        // Expose custom_name as display_name so we can use custom display names within project cards
        setAllProjects(raw.map((p) => ({ ...p, display_name: p.custom_name || p.name })));
      })
      .catch((err) => showToast(err.message, 'error'))
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

  // When selected username changes, fetch only the projects that contributor is linked to
  useEffect(() => {
    if (!username) {
      setUserProjects([]);
      setExcludedProjectIds([]);
      return;
    }
    setIsLoadingUserProjects(true);
    setExcludedProjectIds([]);
    axios
      .get(`${API_BASE_URL}/rank-projects`, {
        params: { mode: 'contributor', contributor_name: username },
      })
      .then((res) => {
        const ranked = Array.isArray(res.data) ? res.data : [];
        const rankedNames = new Set(ranked.map((r) => r.project));
        setUserProjects(allProjects.filter((p) => rankedNames.has(p.name)));
      })
      .catch(() => setUserProjects([]))
      .finally(() => setIsLoadingUserProjects(false));
  }, [username, allProjects]);

  const toggleExclude = (id) => {
    setExcludedProjectIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  };

  const handleGenerate = async () => {
    if (!username) {
      showToast('Please select a username.', 'error');
      return;
    }
    const eligible = userProjects.filter(
      (p) => !excludedProjectIds.includes(p.id ?? p.project_id)
    );
    if (eligible.length < 3) {
      showToast('You need at least 3 projects to generate a portfolio. Adjust your inclusion list or scan more projects.', 'error');
      return;
    }
    setIsGenerating(true);
    setIncludedProjects(eligible);

    // Generate the portfolio and aggregate required data
    try {
      const genRes = await axios.post(`${API_BASE_URL}/portfolio/generate`, {
        username,
        save_to_db: true,
        confidence_level: 'high',
      });
      const { portfolio_id } = genRes.data;
      setPortfolioId(portfolio_id);

      // Retrieve all relevant data for the web portfolio (fetched in parallel)
      const [metaRes, showcaseRes, heatmapRes, timelineRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/portfolio/${portfolio_id}`),
        axios.get(`${API_BASE_URL}/web/portfolio/${portfolio_id}/showcase?limit=3`),
        axios.get(`${API_BASE_URL}/web/portfolio/${portfolio_id}/heatmap?granularity=day`),
        axios.get(`${API_BASE_URL}/web/portfolio/${portfolio_id}/timeline?granularity=month`),
      ]);

      setPortfolioMeta(metaRes.data);
      setHeatmapData(heatmapRes.data);
      setTimelineData(timelineRes.data.timeline || []);

      // Fetch per-project detail in parallel to get llm_summary text for card footers.
      // Failures are silently swallowed so they don't block portfolio generation.
      const detailResults = await Promise.allSettled(
        eligible.map((p) => axios.get(`${API_BASE_URL}/projects/${p.id ?? p.project_id}`))
      );
      const detailMap = {};
      detailResults.forEach((result, i) => {
        const id = eligible[i].id ?? eligible[i].project_id;
        if (result.status === 'fulfilled') {
          detailMap[id] = result.value.data ?? null;
        }
      });
      setProjectDetails(detailMap);

      // Auto-star the top 3 ranked projects that are in the "eligible" set
      const eligibleNames = new Set(eligible.map((p) => p.display_name ?? p.name));
      const topThree = (showcaseRes.data.projects || [])
        .filter((p) => eligibleNames.has(p.name ?? p.project ?? p.display_name))
        .slice(0, MAX_FEATURED)
        .map((p) => p.name ?? p.project ?? p.display_name);
      // Fall back to first 3 eligible projects if scores are missing
      const initialStars = topThree.length > 0
        ? topThree
        : eligible.slice(0, MAX_FEATURED).map((p) => p.display_name ?? p.name);
      setFeaturedIds(new Set(initialStars));

      // Transition to dashboard phase after all data is loaded
      setPhase('dashboard');
    } catch (err) {
      const detail = err?.response?.data?.detail;
      showToast(detail || err.message || 'Failed to generate portfolio.', 'error');
    } finally {
      setIsGenerating(false);
    }
  };

  // Error handling for starring/unstarring projects
  const handleStar = (name) => {
    if (!featuredIds.has(name) && featuredIds.size >= MAX_FEATURED) {
      showToast(`You can only feature ${MAX_FEATURED} projects. Unstar one first.`, 'info');
      return;
    }

    // Toggle starred state by adding/removing from the set
    setFeaturedIds((prev) => {
      if (prev.has(name)) {
        const next = new Set(prev);
        next.delete(name);
        return next;
      }
      return new Set([...prev, name]);
    });
  };

  // Reset web portfolio state and go back to setup form
  const handleBackToSetup = () => {
    setPhase('setup');
    setPortfolioId(null);
    setPortfolioMeta(null);
    setHeatmapData({ cells: [], max_value: 0 });
    setTimelineData([]);
    setProjectSearch('');
    setIncludedProjects([]);
    setFeaturedIds(new Set());
    setProjectDetails({});
    setExpandedProjectId(null);
    clearTimeout(toastTimer.current);
    setToast(null);
  };

  // Store display name for web portfolio header
  const displayName = legalName.trim() || username;

  // Summary line in portfolio header (e.g. "XX projects | Generated on X/X/XXXX") [TODO: update later to be a user-centric summary]
  const headerSummary = portfolioMeta
    ? `${portfolioMeta.metadata.project_count} projects | Generated on ${new Date(portfolioMeta.generated_at).toLocaleDateString()}`
    : '';

  // Web portfolio dashboard phase
  if (phase === 'dashboard') {
    return (
      <div className="page-shell portfolio-page">
        <header className="app-header">
          <h1 style={{ fontWeight: 'bold' }}>Web Portfolio</h1>
          <h2 style={{ color: '#bbbbbb' }}>Private / Preview Mode - Make edits before viewing/exporting the final version</h2>
        </header>

        <div className="portfolio-toolbar">
          <button type="button" className="secondary" onClick={handleBackToSetup}>
            Back to Setup
          </button>
        </div>

        {/* Global toast notification */}
        {toast && (
          <div className={`app-toast app-toast--${toast.type}`} role={toast.type === 'error' ? 'alert' : 'status'}>
            {toast.message}
          </div>
        )}

        <div className="portfolio-dashboard">
          {/* Header tile */}
          <section className="portfolio-header">
            <p className="portfolio-dashboard-name">{displayName}</p>
            <p className="portfolio-header-summary">{headerSummary}</p>
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
            <div className="featured-card-container">
              {includedProjects
                .filter((p) => featuredIds.has(p.display_name ?? p.name))
                .map((p) => {
                  const name = p.display_name ?? p.name ?? '(unnamed)';
                  const projectId = p.id ?? p.project_id;
                  const thumbSrc = getThumbnailSrc(projectId, p.thumbnail_path);
                  const summary = projectDetails[projectId]?.llm_summary?.text ?? null;
                  return (
                    <div key={projectId ?? name} className="project-card-16-9 featured" onClick={() => setExpandedProjectId(projectId)} style={{ cursor: 'pointer' }}>
                      <div className="project-card-header">
                        <span className="project-card-name">{name}</span>
                        {showStars && (
                          <button
                            type="button"
                            className="star-btn starred"
                            onClick={(e) => { e.stopPropagation(); handleStar(name); }}
                            aria-label="Unfeature project"
                            title="Remove from Featured"
                          >
                            ★
                          </button>
                        )}
                      </div>
                      <div className="project-card-image">
                        {thumbSrc
                          ? <img src={thumbSrc} alt={`${name} thumbnail`} />
                          : <span className="project-card-no-thumb">No thumbnail</span>}
                      </div>
                      <div className="project-card-footer">
                        <p className="project-card-summary">
                          {summary ?? 'No summary available.'}
                        </p>
                      </div>
                    </div>
                  );
                })}
              {featuredIds.size === 0 && (
                <p className="tile-placeholder-text" style={{ margin: 0 }}>
                  Star projects below to feature them here.
                </p>
              )}
            </div>
          </section>

          {/* All projects tile */}
          <section className="portfolio-tile">
            <div className="all-projects-header">
              <h3 className="tile-heading">All Projects</h3>
              <div className="all-projects-search">
                <input
                  type="text"
                  className="portfolio-input"
                  placeholder="Search projects..."
                  value={projectSearch}
                  onChange={(e) => setProjectSearch(e.target.value)}
                />
              </div>
            </div>
            <div className="all-projects-card-container">
              {includedProjects
                .filter((p) => {
                  const name = p.display_name ?? p.name ?? '';
                  return name.toLowerCase().includes(projectSearch.toLowerCase());
                })
                .map((p) => {
                  const name = p.display_name ?? p.name ?? '(unnamed)';
                  const isStarred = featuredIds.has(name);
                  const projectId = p.id ?? p.project_id;
                  const thumbSrc = getThumbnailSrc(projectId, p.thumbnail_path);
                  const summary = projectDetails[projectId]?.llm_summary?.text ?? null;
                  return (
                    <div key={projectId ?? name} className="project-card-16-9 all-projects" onClick={() => setExpandedProjectId(projectId)} style={{ cursor: 'pointer' }}>
                      <div className="project-card-header">
                        <span className="project-card-name">{name}</span>
                        {showStars && (
                          <button
                            type="button"
                            className={`star-btn${isStarred ? ' starred' : ''}`}
                            onClick={(e) => { e.stopPropagation(); handleStar(name); }}
                            aria-label={isStarred ? 'Unfeature project' : 'Feature project'}
                            title={isStarred ? 'Remove from Featured' : 'Add to Featured'}
                          >
                            {isStarred ? '★' : '☆'}
                          </button>
                        )}
                      </div>
                      <div className="project-card-image">
                        {thumbSrc
                          ? <img src={thumbSrc} alt={`${name} thumbnail`} />
                          : <span className="project-card-no-thumb">No thumbnail</span>}
                      </div>
                      <div className="project-card-footer">
                        <p className="project-card-summary">
                          {summary ?? 'No summary available.'}
                        </p>
                      </div>
                    </div>
                  );
                })}
            </div>
          </section>
        </div>

        {expandedProjectId != null && (() => {
          const p = includedProjects.find((x) => (x.id ?? x.project_id) === expandedProjectId);
          if (!p) return null;
          return (
            <ProjectModal
              project={p}
              detail={projectDetails[expandedProjectId] ?? null}
              username={username}
              displayName={displayName}
              onClose={() => setExpandedProjectId(null)}
            />
          );
        })()}
      </div>
    );
  }

  // Setup phase
  return (
    <div className="page-shell portfolio-page">
      <header className="app-header">
        <h1 style={{ fontWeight: 'bold' }}>Generate Portfolio</h1>
        <h2 style={{ color: '#bbbbbb' }}>Build a web portfolio from your scanned projects.</h2>
      </header>

      <div className="portfolio-toolbar">
        <button type="button" className="secondary" onClick={onBack}>
          Back to Main Menu
        </button>
      </div>

      <section className="portfolio-setup-panel">
        <h2>Portfolio Setup</h2>

        {isLoadingProjects && <p>Loading projects...</p>}

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
                placeholder="e.g. John Doe"
              />
              <span className="portfolio-hint">
                Shown in the portfolio header instead of your GitHub username.
              </span>
            </label>

            <fieldset className="portfolio-exclusion-fieldset">
              <legend>Included Projects</legend>
              {!username && (
                <p className="portfolio-hint">Select a username above to see their projects.</p>
              )}
              {username && isLoadingUserProjects && (
                <p className="portfolio-hint">Loading projects…</p>
              )}
              {username && !isLoadingUserProjects && userProjects.length < 3 && (
                <p className="portfolio-notice" style={{ margin: '0.3rem 0' }}>
                  {userProjects.length === 0
                    ? `No projects found for "${username}". Try a different contributor.`
                    : `Only ${userProjects.length} project(s) found for "${username}". At least 3 are needed.`}
                </p>
              )}
              {username && !isLoadingUserProjects && userProjects.length >= 3 && (
                <>
                  <p className="portfolio-hint">
                    Uncheck any projects you do NOT want included in your portfolio.
                  </p>
                  {userProjects.map((project) => {
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
                </>
              )}
            </fieldset>

            {isGenerating && (
              <div className="portfolio-generating">
                <div className="portfolio-spinner" />
                <p>Generating your portfolio…</p>
              </div>
            )}

            <div className="portfolio-form-actions">
              <button type="button" onClick={handleGenerate} disabled={isGenerating}>
                {isGenerating ? 'Generating…' : 'Generate Web Portfolio'}
              </button>
            </div>
          </div>
        )}
      </section>

      {/** Global toast notification */}
      {toast && (
        <div className={`app-toast app-toast--${toast.type}`} role={toast.type === 'error' ? 'alert' : 'status'}>
          {toast.message}
        </div>
      )}
    </div>
  );
}

export default PortfolioPage;
