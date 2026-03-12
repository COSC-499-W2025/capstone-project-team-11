import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { API_BASE_URL } from './api';

function RankProjectsPage({ onBack }) {
  const [projects, setProjects] = useState([]);
  const [limit, setLimit] = useState(10);
  const [mode, setMode] = useState('project');
  const [contributorName, setContributorName] = useState('');
  const [contributorOptions, setContributorOptions] = useState([]);
  const [rankingMode, setRankingMode] = useState('importance');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  // Custom ranking state
  const [savedRankings, setSavedRankings] = useState([]);
  const [expandedRanking, setExpandedRanking] = useState(null);
  const [expandedProjects, setExpandedProjects] = useState([]);
  const [customProjects, setCustomProjects] = useState([]);
  const [draggedProjectIndex, setDraggedProjectIndex] = useState(null);
  const [newRankingName, setNewRankingName] = useState('');
  const [newRankingDesc, setNewRankingDesc] = useState('');
  const [customError, setCustomError] = useState('');

  const formatDate = (value) => {
    if (!value) {
      return '--';
    }
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
      return value;
    }
    return date.toLocaleDateString();
  };

  const fetchRankedProjects = async (nextLimit = limit) => {
    setIsLoading(true);
    setError('');

    const sortMode = rankingMode;
    const chronologicalOrder = 'desc';
    const effectiveMode = rankingMode === 'importance' ? mode : 'project';

    if (effectiveMode === 'contributor' && !contributorName.trim()) {
      setError('Enter a contributor name for contributor importance mode.');
      setProjects([]);
      setIsLoading(false);
      return;
    }

    try {
      const response = await axios.get(`${API_BASE_URL}/rank-projects`, {
        params: {
          mode: effectiveMode,
          contributor_name: effectiveMode === 'contributor' ? contributorName.trim() : undefined,
          limit: nextLimit,
          sort_mode: sortMode,
          chronological_order: chronologicalOrder,
        },
      });

      const nextProjects = Array.isArray(response.data) ? response.data : [];
      setProjects(nextProjects);
      setCustomProjects(nextProjects.map((project) => project.project));
    } catch (err) {
      const detail = err?.response?.data?.detail;
      setError(`Failed to load ranked projects: ${detail || err.message}`);
      setProjects([]);
      setCustomProjects([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCustomDragStart = (index) => {
    setDraggedProjectIndex(index);
  };

  const handleCustomDrop = (targetIndex) => {
    setCustomProjects((current) => {
      if (draggedProjectIndex === null || draggedProjectIndex === targetIndex) {
        return current;
      }

      const next = [...current];
      const [item] = next.splice(draggedProjectIndex, 1);
      next.splice(targetIndex, 0, item);
      return next;
    });
    setDraggedProjectIndex(null);
  };

  const handleCustomDragEnd = () => {
    setDraggedProjectIndex(null);
  };

  const resetCustomProjects = () => {
    setCustomProjects(projects.map((project) => project.project));
  };

  const fetchSavedRankings = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/custom-rankings`);
      setSavedRankings(Array.isArray(res.data) ? res.data : []);
    } catch { setSavedRankings([]); }
  };

  const handleCreateRanking = async () => {
    setCustomError('');
    const name = newRankingName.trim();
    if (!name) { setCustomError('Title is required.'); return; }
    if (customProjects.length === 0) { setCustomError('Run a ranking first so there are projects to save.'); return; }
    try {
      await axios.post(`${API_BASE_URL}/custom-rankings`, {
        name,
        description: newRankingDesc.trim(),
        projects: customProjects,
      });
      setNewRankingName('');
      setNewRankingDesc('');
      fetchSavedRankings();
    } catch (err) {
      setCustomError(err?.response?.data?.detail || err.message);
    }
  };

  const handleDeleteRanking = async (name) => {
    try {
      await axios.delete(`${API_BASE_URL}/custom-rankings/${encodeURIComponent(name)}`);
      if (expandedRanking === name) { setExpandedRanking(null); setExpandedProjects([]); }
      fetchSavedRankings();
    } catch { /* ignore */ }
  };

  const handleToggleExpand = async (name) => {
    if (expandedRanking === name) { setExpandedRanking(null); setExpandedProjects([]); return; }
    try {
      const res = await axios.get(`${API_BASE_URL}/custom-rankings/${encodeURIComponent(name)}`);
      setExpandedProjects(res.data.projects || []);
      setExpandedRanking(name);
    } catch { setExpandedRanking(null); setExpandedProjects([]); }
  };

  useEffect(() => {
    fetchRankedProjects();
    fetchSavedRankings();
    // Intentionally run once on page load.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const loadContributors = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/contributors`);
        const contributors = Array.isArray(response.data) ? response.data : [];
        setContributorOptions(contributors);
        if (!contributorName && contributors.length > 0) {
          setContributorName(contributors[0]);
        }
      } catch {
        setContributorOptions([]);
      }
    };

    loadContributors();
  }, []);

  const topScore =
    projects.length > 0
      ? Number(mode === 'contributor' ? projects[0].score || 0 : projects[0].top_score || 0)
      : 0;

  return (
    <div className="page-shell rank-projects-page">
      <header className="app-header">
        <h1>Rank Projects</h1>
        <p>Project-level importance ranking based on contribution coverage and collaboration metrics.</p>
      </header>

      <div className="rank-toolbar">
        <button type="button" className="secondary" onClick={onBack}>
          Back to Main Menu
        </button>

        <label className="rank-limit-group" htmlFor="rank-limit">
          <span>Show Top</span>
          <input
            id="rank-limit"
            type="number"
            min="1"
            max="200"
            value={limit}
            onChange={(event) => {
              const nextValue = Number(event.target.value);
              setLimit(Number.isFinite(nextValue) && nextValue > 0 ? nextValue : 1);
            }}
          />
        </label>

        <label className="rank-view-group" htmlFor="rank-mode">
          <span>Ranking Mode</span>
          <select
            id="rank-mode"
            value={rankingMode}
            onChange={(event) => setRankingMode(event.target.value)}
          >
            <option value="importance">Project Importance</option>
            <option value="chronological">Chronological</option>
          </select>
        </label>

        {rankingMode === 'importance' ? (
          <label className="rank-view-group" htmlFor="rank-scope">
            <span>Importance Scope</span>
            <select
              id="rank-scope"
              value={mode}
              onChange={(event) => setMode(event.target.value)}
            >
              <option value="project">All Projects</option>
              <option value="contributor">Per User</option>
            </select>
          </label>
        ) : null}

        {rankingMode === 'importance' && mode === 'contributor' ? (
          <label className="rank-contributor-group" htmlFor="rank-contributor-input">
            <span>Contributor</span>
            <select
              id="rank-contributor-input"
              value={contributorName}
              onChange={(event) => setContributorName(event.target.value)}
            >
              {contributorOptions.length === 0 ? <option value="">No contributors found</option> : null}
              {contributorOptions.map((name) => (
                <option key={name} value={name}>
                  {name}
                </option>
              ))}
            </select>
          </label>
        ) : null}

        <button
          type="button"
          onClick={() => fetchRankedProjects(limit)}
          disabled={isLoading}
        >
          {isLoading ? 'Loading...' : 'Refresh Ranking'}
        </button>
      </div>

      {error ? <p className="error-text rank-error">{error}</p> : null}

      <section className="rank-explanation-panel">
        <h2>Scoring Explanation</h2>
        <p>
          Importance score is weighted as <strong>0.6 * coverage</strong> +{' '}
          <strong>0.3 * dominance gap</strong> + <strong>0.1 * team-size factor</strong>.
        </p>
        <p>
          Coverage = contributor file share in a project. Dominance gap rewards clear lead over the
          next contributor. Team-size factor slightly boosts impact in smaller teams.
        </p>
        <p>
          <strong>Project mode</strong> ranks projects by top-contributor impact.{' '}
          <strong>Per-contributor mode</strong> ranks projects by how important they are for one
          selected contributor.
        </p>
      </section>

      <section className="rank-summary-grid">
        <article className="rank-summary-card">
          <h3>Ranked Projects</h3>
          <p className="rank-summary-value">{projects.length}</p>
        </article>
        <article className="rank-summary-card">
          <h3>{mode === 'contributor' ? 'Contributor' : 'Top Project'}</h3>
          <p className="rank-summary-value">
            {rankingMode === 'importance' && mode === 'contributor'
              ? (contributorName.trim() || '--')
              : (projects[0]?.project || '--')}
          </p>
        </article>
        <article className="rank-summary-card">
          <h3>{rankingMode === 'importance' && mode === 'contributor' ? 'Top Project' : 'Top Score'}</h3>
          <p className="rank-summary-value">
            {rankingMode === 'importance' && mode === 'contributor'
              ? (projects[0]?.project || '--')
              : topScore.toFixed(3)}
          </p>
        </article>
      </section>

      <section className="rank-table-panel">
        <h2>Ranking Results</h2>

        {isLoading ? <p>Loading ranking...</p> : null}
        {!isLoading && projects.length === 0 ? <p>No ranked projects found.</p> : null}
        {!isLoading && projects.length > 0 ? (
          <div className="rank-table-wrap">
            <table className="rank-table">
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Project</th>
                  <th>Type</th>
                  <th>Total Files</th>
                  <th>Created</th>
                  <th>First Scan</th>
                  <th>Last Scan</th>
                  <th>Contributors</th>
                  <th>{rankingMode === 'importance' && mode === 'contributor' ? 'Contributor Files' : 'Top Contributor'}</th>
                  <th>{rankingMode === 'importance' && mode === 'contributor' ? 'Coverage' : 'Top Files'}</th>
                  <th>Score</th>
                </tr>
              </thead>
              <tbody>
                {projects.map((project, index) => {
                  const contributorCount = Number(project.contributors_count || 0);
                  const isCollaborative = contributorCount > 1;
                  const topFraction = Number(
                    rankingMode === 'importance' && mode === 'contributor'
                      ? (project.total_files ? (Number(project.contrib_files || 0) / Number(project.total_files || 1)) : 0)
                      : (project.top_fraction || 0)
                  );
                  const topScoreValue = Number(project.top_score || 0);
                  const contributorScore = Number(project.score || 0);

                  return (
                    <tr key={`${project.project}-${index}`}>
                      <td>{index + 1}</td>
                      <td>{project.project}</td>
                      <td>{isCollaborative ? 'Collaborative' : 'Individual'}</td>
                      <td>{project.total_files ?? 0}</td>
                      <td>{formatDate(project.created_at)}</td>
                      <td>{formatDate(project.first_scan)}</td>
                      <td>{formatDate(project.last_scan)}</td>
                      <td>{contributorCount}</td>
                      <td>
                        {rankingMode === 'importance' && mode === 'contributor'
                          ? (project.contrib_files ?? 0)
                          : (project.top_contributor || '--')}
                      </td>
                      <td>{rankingMode === 'importance' && mode === 'contributor' ? `${(topFraction * 100).toFixed(1)}%` : (project.top_contrib_files ?? 0)}</td>
                      <td>{(rankingMode === 'importance' && mode === 'contributor' ? contributorScore : topScoreValue).toFixed(3)}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : null}
      </section>

      {/* ── Create Custom Ranking ────────────────────────── */}
      <section className="rank-table-panel custom-ranking-create">
        <h2>Save as Custom Ranking</h2>
        <p>Arrange the projects into your own order, then save that ranking with a title and short description.</p>
        <div className="custom-ranking-form">
          <label htmlFor="cr-name">
            <span>Title</span>
            <input
              id="cr-name"
              type="text"
              maxLength={120}
              placeholder="e.g. Spring 2026 Top Projects"
              value={newRankingName}
              onChange={(e) => setNewRankingName(e.target.value)}
            />
          </label>
          <label htmlFor="cr-desc">
            <span>Description</span>
            <input
              id="cr-desc"
              type="text"
              maxLength={500}
              placeholder="Short note about this ranking (optional)"
              value={newRankingDesc}
              onChange={(e) => setNewRankingDesc(e.target.value)}
            />
          </label>
          <button type="button" className="secondary" onClick={resetCustomProjects} disabled={projects.length === 0}>
            Reset Order
          </button>
          <button type="button" onClick={handleCreateRanking} disabled={customProjects.length === 0}>
            Create Ranking
          </button>
        </div>
        {customProjects.length > 0 ? (
          <div className="custom-order-editor">
            <div className="custom-order-header">
              <strong>Custom Ranking Order</strong>
              <span>Drag rows up or down to choose each project&apos;s position.</span>
            </div>
            <ol className="custom-order-list">
              {customProjects.map((projectName, index) => (
                <li
                  key={projectName}
                  draggable
                  className={draggedProjectIndex === index ? 'custom-order-item dragging' : 'custom-order-item'}
                  onDragStart={() => handleCustomDragStart(index)}
                  onDragOver={(event) => event.preventDefault()}
                  onDrop={() => handleCustomDrop(index)}
                  onDragEnd={handleCustomDragEnd}
                >
                  <span className="custom-order-rank">{index + 1}</span>
                  <div className="custom-order-content">
                    <strong>{projectName}</strong>
                    <span>Drop it anywhere in the list to change its position.</span>
                  </div>
                  <span className="custom-drag-pill" aria-hidden="true">
                    <span className="custom-drag-handle">::</span>
                    Drag
                  </span>
                </li>
              ))}
            </ol>
          </div>
        ) : null}
        {customError ? <p className="error-text rank-error">{customError}</p> : null}
      </section>

      {/* ── Saved Custom Rankings ────────────────────────── */}
      {savedRankings.length > 0 ? (
        <section className="rank-table-panel custom-ranking-list">
          <h2>Saved Custom Rankings</h2>
          {savedRankings.map((r) => (
            <div key={r.name} className="custom-ranking-card">
              <div className="custom-ranking-card-header">
                <div>
                  <strong>{r.name}</strong>
                  {r.description ? <span className="custom-ranking-desc">{r.description}</span> : null}
                  <span className="custom-ranking-date">Created {formatDate(r.created_at)}</span>
                </div>
                <div className="custom-ranking-actions">
                  <button type="button" className="secondary" onClick={() => handleToggleExpand(r.name)}>
                    {expandedRanking === r.name ? 'Collapse' : 'View'}
                  </button>
                  <button type="button" className="danger" onClick={() => handleDeleteRanking(r.name)}>
                    Delete
                  </button>
                </div>
              </div>
              {expandedRanking === r.name && expandedProjects.length > 0 ? (
                <div className="rank-table-wrap">
                  <table className="rank-table">
                    <thead>
                      <tr><th>Rank</th><th>Project</th></tr>
                    </thead>
                    <tbody>
                      {expandedProjects.map((proj, i) => (
                        <tr key={proj}><td>{i + 1}</td><td>{proj}</td></tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : null}
            </div>
          ))}
        </section>
      ) : null}
    </div>
  );
}

export default RankProjectsPage;
