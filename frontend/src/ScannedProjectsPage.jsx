import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { API_BASE_URL } from './api';

function getThumbnailSrc(projectId, path) {
  if (!projectId || !path) return '';
  if (/^https?:\/\//i.test(path) || /^data:/i.test(path)) {
    return path;
  }
  return `${API_BASE_URL}/projects/${projectId}/thumbnail/image?v=${encodeURIComponent(path)}`;
}

function formatDate(value) {
  if (!value) return 'Not available';
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return String(value);
  return parsed.toLocaleString();
}

function formatRoleConfidence(value) {
  if (typeof value !== 'number' || Number.isNaN(value)) {
    return '0%';
  }
  return `${Math.round(value * 100)}%`;
}

function getProjectId(project) {
  return project?.project_id ?? project?.id ?? null;
}

function getProjectName(project, fallbackId) {
  return (
    project?.custom_name ??
    project?.display_name ??
    project?.name ??
    project?.project_name ??
    `Project ${fallbackId ?? 'Unknown'}`
  );
}

function getEvidenceTitle(item, index) {
  if (typeof item === 'string') return item;
  return item?.title ?? item?.description ?? item?.name ?? item?.value ?? `Evidence ${index + 1}`;
}

function getEvidenceMeta(item) {
  if (!item || typeof item !== 'object') return '';
  return item.type ?? item.kind ?? item.category ?? item.source ?? '';
}

function getEvidenceDescription(item) {
  if (!item || typeof item !== 'object') return '';
  return item.description ?? item.value ?? item.source ?? item.url ?? '';
}

function ScannedProjectsPage({ onBack }) {
  const [projects, setProjects] = useState([]);
  const [selectedProjectId, setSelectedProjectId] = useState(null);
  const [selectedProject, setSelectedProject] = useState(null);
  const [projectQuery, setProjectQuery] = useState('');
  const [activePanel, setActivePanel] = useState('overview');
  const [isLoadingProjects, setIsLoadingProjects] = useState(true);
  const [isLoadingDetails, setIsLoadingDetails] = useState(false);
  const [isUpdatingThumbnail, setIsUpdatingThumbnail] = useState(false);
  const [projectsError, setProjectsError] = useState('');
  const [detailsError, setDetailsError] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [isSavingProject, setIsSavingProject] = useState(false);
  const [editError, setEditError] = useState('');
  const [editCustomName, setEditCustomName] = useState('');
  const [editRepoUrl, setEditRepoUrl] = useState('');
  const [editThumbnailPath, setEditThumbnailPath] = useState('');
  const [editSummaryText, setEditSummaryText] = useState('');

  useEffect(() => {
    const loadProjects = async () => {
      setIsLoadingProjects(true);
      setProjectsError('');

      try {
        const response = await axios.get(`${API_BASE_URL}/projects`);
        const projectList = Array.isArray(response.data) ? response.data : [];
        setProjects(projectList);

        if (projectList.length > 0) {
          const firstProjectId = getProjectId(projectList[0]);
          setSelectedProjectId((current) => current ?? firstProjectId);
        }
      } catch (err) {
        setProjectsError(`Failed to load projects: ${err.message}`);
      } finally {
        setIsLoadingProjects(false);
      }
    };

    loadProjects();
  }, []);

  useEffect(() => {
    if (selectedProjectId == null) {
      setSelectedProject(null);
      setIsEditing(false);
      return;
    }

    const loadProjectDetails = async () => {
      setIsLoadingDetails(true);
      setDetailsError('');

      try {
        const response = await axios.get(`${API_BASE_URL}/projects/${selectedProjectId}`);
        setSelectedProject(response.data);
      } catch (err) {
        setDetailsError(`Failed to load project details: ${err.message}`);
      } finally {
        setIsLoadingDetails(false);
      }
    };

    loadProjectDetails();
  }, [selectedProjectId]);

   useEffect(() => {
    if (selectedProject && isEditing) {
      setEditCustomName(selectedProject.project?.custom_name || '');
      setEditRepoUrl(selectedProject.project?.repo_url || '');
      setEditThumbnailPath(selectedProject.project?.thumbnail_path || '');
      setEditSummaryText(selectedProject.llm_summary?.text || '');
      setEditError('');
    }
  }, [selectedProject, isEditing]);

  const refreshProjectData = async () => {
    const [detailsResponse, listResponse] = await Promise.all([
      axios.get(`${API_BASE_URL}/projects/${selectedProjectId}`),
      axios.get(`${API_BASE_URL}/projects`),
    ]);
    setSelectedProject(detailsResponse.data);
    setProjects(Array.isArray(listResponse.data) ? listResponse.data : []);
  };

    const handleEditProject = () => {
    if (!selectedProject) return;
    setEditCustomName(selectedProject.project?.custom_name || '');
    setEditRepoUrl(selectedProject.project?.repo_url || '');
    setEditThumbnailPath(selectedProject.project?.thumbnail_path || '');
    setEditSummaryText(selectedProject.llm_summary?.text || '');
    setEditError('');
    setIsEditing(true);
  };


    const handleCancelEdit = () => {
    setEditCustomName(selectedProject?.project?.custom_name || '');
    setEditRepoUrl(selectedProject?.project?.repo_url || '');
    setEditThumbnailPath(selectedProject?.project?.thumbnail_path || '');
    setEditSummaryText(selectedProject?.llm_summary?.text || '');
    setEditError('');
    setIsEditing(false);
  };

  const handleSaveProject = async () => {
  if (selectedProjectId == null || !selectedProject) return;

  const trimmedCustomName = editCustomName.trim();
  const trimmedRepoUrl = editRepoUrl.trim();
  const trimmedThumbnailPath = editThumbnailPath.trim();
  const trimmedSummaryText = editSummaryText.trim();

  try {
    setIsSavingProject(true);
    setEditError('');

    await axios.patch(`${API_BASE_URL}/projects/${selectedProjectId}`, {
      custom_name: trimmedCustomName,
      repo_url: trimmedRepoUrl,
      thumbnail_path: trimmedThumbnailPath,
      summary_text: trimmedSummaryText,
    });

    setIsEditing(false);
    await refreshProjectData();
  } catch (error) {
    console.error('Failed to update project:', error);
    setEditError('Failed to update project.');
  } finally {
    setIsSavingProject(false);
  }
};

  const handleDeleteProject = async () => {
    if (selectedProjectId == null) return;

    const projectName = getProjectName(selectedProject?.project, selectedProjectId);
    const confirmed = window.confirm(`Are you sure you want to delete "${projectName}"?`);
    if (!confirmed) return;

    try {
      await axios.delete(`${API_BASE_URL}/projects/${selectedProjectId}`);
      window.alert('Project deleted successfully');

      const updatedProjects = projects.filter((project) => getProjectId(project) !== selectedProjectId);
      setProjects(updatedProjects);
      setIsEditing(false);

      if (updatedProjects.length > 0) {
        setSelectedProjectId(getProjectId(updatedProjects[0]));
      } else {
        setSelectedProjectId(null);
        setSelectedProject(null);
      }
    } catch (error) {
      console.error('Failed to delete project:', error);
      window.alert('Failed to delete project.');
    }
  };

  const handleUpdateThumbnail = async () => {
    if (selectedProjectId == null || !selectedProject?.project) return;

    const nextThumbnailPath = await window.api?.openThumbnailDialog?.();
    if (!nextThumbnailPath) return;

    try {
      setIsUpdatingThumbnail(true);
      await axios.patch(`${API_BASE_URL}/projects/${selectedProjectId}`, {
        thumbnail_path: nextThumbnailPath,
      });

      if (isEditing) {
        setEditThumbnailPath(nextThumbnailPath);
      }

      await refreshProjectData();
    } catch (error) {
      console.error('Failed to update project thumbnail:', error);
      window.alert('Failed to update project thumbnail.');
    } finally {
      setIsUpdatingThumbnail(false);
    }
  };

  const filteredProjects = projects.filter((project) => {
    const projectId = getProjectId(project);
    const projectName = getProjectName(project, projectId);
    const query = projectQuery.trim().toLowerCase();
    if (!query) return true;
    return projectName.toLowerCase().includes(query) || String(projectId ?? '').includes(query);
  });

  const selectedProjectMeta = selectedProject?.project ?? {};
  const selectedProjectName = getProjectName(selectedProjectMeta, selectedProjectId);
  const thumbnailSrc = getThumbnailSrc(selectedProjectId, selectedProjectMeta.thumbnail_path);
  const languages = Array.isArray(selectedProject?.languages) ? selectedProject.languages : [];
  const skills = Array.isArray(selectedProject?.skills) ? selectedProject.skills : [];
  const contributors = Array.isArray(selectedProject?.contributors) ? selectedProject.contributors : [];
  const scans = Array.isArray(selectedProject?.scans) ? selectedProject.scans : [];
  const evidence = Array.isArray(selectedProject?.evidence) ? selectedProject.evidence : [];
  const contributorRoles = Array.isArray(selectedProject?.contributor_roles?.contributors)
    ? selectedProject.contributor_roles.contributors
    : [];
  const extensionEntries = Object.entries(selectedProject?.files_summary?.extensions ?? {})
    .sort((a, b) => Number(b[1]) - Number(a[1]));
  const maxExtensionCount = extensionEntries[0] ? Number(extensionEntries[0][1]) || 1 : 1;
  const statCards = [
    { label: 'Files Indexed', value: selectedProject?.files_summary?.total_files ?? 0, tone: 'cyan' },
    { label: 'Languages', value: languages.length, tone: 'green' },
    { label: 'Skills', value: skills.length, tone: 'amber' },
    { label: 'Evidence Items', value: evidence.length, tone: 'red' },
  ];

  return (
    <div className="page-shell scanned-projects-page">
      <header className="app-header">
        <h1>Scanned Projects</h1>
        <p>Review scanned repositories, compare project signals, and inspect saved evidence.</p>
      </header>

      <div className="scanned-projects-toolbar">
        <button type="button" className="secondary" onClick={onBack}>
          Back to Main Menu
        </button>
      </div>

      <div className="scanned-projects-overview">
        <div className="overview-panel overview-panel-accent">
          <span className="overview-eyebrow">Project Vault</span>
          <h2>{projects.length} project{projects.length === 1 ? '' : 's'} archived</h2>
          <p>Search the archive, review technical signals, and inspect contributor role context.</p>
        </div>
        <div className="overview-panel">
          <span className="overview-eyebrow">Visible Now</span>
          <h2>{filteredProjects.length}</h2>
          <p>Projects matching your current search query.</p>
        </div>
        <div className="overview-panel">
          <span className="overview-eyebrow">Latest Activity</span>
          <h2>{scans[0]?.scanned_at ? formatDate(scans[0].scanned_at) : 'No scans yet'}</h2>
          <p>Most recent recorded scan for the selected project.</p>
        </div>
      </div>

      <div className="scanned-projects-layout">
        <aside className="projects-list-panel">
          <div className="projects-panel-header">
            <div>
              <span className="panel-eyebrow">Library</span>
              <h2>Project Explorer</h2>
            </div>
            <span className="projects-count-pill">{filteredProjects.length}</span>
          </div>

          <label className="projects-search" htmlFor="project-search">
            <span>Search projects</span>
            <input
              id="project-search"
              type="text"
              value={projectQuery}
              onChange={(event) => setProjectQuery(event.target.value)}
              placeholder="Filter by name or ID"
            />
          </label>

          {isLoadingProjects && <p>Loading projects...</p>}
          {projectsError && <p className="error-text">{projectsError}</p>}

          {!isLoadingProjects && !projectsError && projects.length === 0 && (
            <div className="empty-state-card">
              <h3>No scanned projects yet</h3>
              <p>Scan a project first to see it here.</p>
            </div>
          )}

          {!isLoadingProjects && !projectsError && projects.length > 0 && filteredProjects.length === 0 && (
            <div className="empty-state-card compact">
              <h3>No matching projects</h3>
              <p>Try a different name or clear the search field.</p>
            </div>
          )}

          {!isLoadingProjects && !projectsError && filteredProjects.length > 0 && (
            <div className="projects-list">
              {filteredProjects.map((project, index) => {
                const projectId = getProjectId(project);
                const projectName = getProjectName(project, projectId);
                const isSelected = selectedProjectId === projectId;

                return (
                  <button
                    key={projectId}
                    type="button"
                    className={`project-list-item ${isSelected ? 'is-selected' : ''}`}
                    onClick={() => {
                      setSelectedProjectId(projectId);
                      setActivePanel('overview');
                    }}
                  >
                    <span className="project-list-index">{String(index + 1).padStart(2, '0')}</span>
                    <div className="project-list-copy">
                      <span className="project-list-title">{projectName}</span>
                      <span className="project-list-subtitle">Project ID {projectId}</span>
                    </div>
                    <span className="project-list-arrow" aria-hidden="true">
                      {isSelected ? '●' : '○'}
                    </span>
                  </button>
                );
              })}
            </div>
          )}
        </aside>

        <section className="project-details-panel">
          <div className="projects-panel-header">
            <div>
              <span className="panel-eyebrow">Inspector</span>
              <h2>Project Command Center</h2>
            </div>
            {selectedProjectId != null ? <span className="projects-count-pill">ID {selectedProjectId}</span> : null}
          </div>

          {isLoadingDetails && <p>Loading project details...</p>}
          {detailsError && <p className="error-text">{detailsError}</p>}

          {!isLoadingDetails && !detailsError && selectedProject && (
            <div className="project-details-stack">
              <div className="project-hero-card">
                <div className="project-hero-copy">
                  <span className="panel-eyebrow">Selected Project</span>
                  <h3>{selectedProjectName}</h3>
                  <p>Inspect the project profile, saved summary, contributor roles, and scan evidence in one workspace.</p>
                </div>

                {selectedProjectMeta.thumbnail_path ? (
                  <div className="project-thumbnail-card">
                    <span className="panel-eyebrow">Thumbnail</span>
                    <img src={thumbnailSrc} alt={`${selectedProjectName} thumbnail`} className="project-thumbnail-image" />
                  </div>
                ) : null}

                <div className="project-hero-meta">
                  <div className="hero-meta-pill">
                    <span>Created</span>
                    <strong>{formatDate(selectedProjectMeta.created_at)}</strong>
                  </div>
                  <div className="hero-meta-pill">
                    <span>Repo</span>
                    <strong>{selectedProjectMeta.repo_url ? 'Linked' : 'Not linked'}</strong>
                  </div>
                  <div className="hero-meta-pill">
                    <span>Last Scan</span>
                    <strong>{scans[0]?.scanned_at ? formatDate(scans[0].scanned_at) : 'Pending'}</strong>
                  </div>
                </div>

                <div className="project-hero-actions">
                  <button type="button" className="danger" onClick={handleDeleteProject}>Delete Project</button>
                  <button
                    type="button"
                    className="hero-action-button"
                    onClick={handleUpdateThumbnail}
                    disabled={isUpdatingThumbnail}
                  >
                    {isUpdatingThumbnail
                      ? 'Saving Thumbnail...'
                      : (selectedProjectMeta.thumbnail_path ? 'Change Thumbnail' : 'Add Thumbnail')}
                  </button>
                  {selectedProjectMeta.repo_url ? (
                    <a className="hero-action-button" href={selectedProjectMeta.repo_url} target="_blank" rel="noreferrer">
                      Open Repository
                    </a>
                  ) : null}
                </div>
              </div>

              <div className="project-stat-grid">
                {statCards.map((card) => (
                  <article key={card.label} className={`project-stat-card tone-${card.tone}`}>
                    <span>{card.label}</span>
                    <strong>{card.value}</strong>
                  </article>
                ))}
              </div>

              <div className="project-panel-tabs" role="tablist" aria-label="Project detail panels">
                {['overview', 'signals', 'contributors', 'activity'].map((panel) => (
                  <button
                    key={panel}
                    type="button"
                    role="tab"
                    aria-selected={activePanel === panel}
                    className={`project-panel-tab ${activePanel === panel ? 'is-active' : ''}`}
                    onClick={() => setActivePanel(panel)}
                  >
                    {panel}
                  </button>
                ))}
              </div>

              {activePanel === 'overview' ? (
                <div className="detail-grid">
                  <article className="detail-card detail-card-wide">
                    <div className="detail-card-header">
                      <div>
                        <span className="panel-eyebrow">Summary</span>
                        <h4>Project Snapshot</h4>
                      </div>
                      <button type="button" className="hero-action-button" onClick={handleEditProject}>Edit Project</button>
                    </div>
                    <div className="metadata-grid">
                      <div className="detail-row">
                        <strong>Project ID</strong>
                        <span>{selectedProjectMeta.id ?? selectedProjectId}</span>
                      </div>
                      <div className="detail-row">
                        <strong>Display Name</strong>
                        <span>{selectedProjectMeta.custom_name || 'Not set'}</span>
                      </div>
                      <div className="detail-row">
                        <strong>Thumbnail Path</strong>
                        <span>{selectedProjectMeta.thumbnail_path || 'Not available'}</span>
                      </div>
                      <div className="detail-row">
                        <strong>Repository URL</strong>
                        <span>{selectedProjectMeta.repo_url || 'Not available'}</span>
                      </div>
                    </div>

                                        {isEditing ? (
                      <div className="edit-project-panel">
                        <div className="detail-card-header">
                          <span className="panel-eyebrow">Edit</span>
                          <h4>Edit Project Info</h4>
                        </div>

                        <label className="edit-field" htmlFor="edit-custom-name">
                          <span>Display Name</span>
                          <input
                            id="edit-custom-name"
                            type="text"
                            value={editCustomName}
                            onChange={(e) => setEditCustomName(e.target.value)}
                            className="detail-input"
                          />
                        </label>

                        <label className="edit-field" htmlFor="edit-repo-url">
                          <span>Repo URL</span>
                          <input
                            id="edit-repo-url"
                            type="text"
                            value={editRepoUrl}
                            onChange={(e) => setEditRepoUrl(e.target.value)}
                            className="detail-input"
                          />
                        </label>

                        <label className="edit-field" htmlFor="edit-thumbnail-path">
                          <span>Thumbnail Path</span>
                          <input
                            id="edit-thumbnail-path"
                            type="text"
                            value={editThumbnailPath}
                            onChange={(e) => setEditThumbnailPath(e.target.value)}
                            className="detail-input"
                          />
                        </label>

                        <label className="edit-field" htmlFor="edit-summary-text">
                          <span>LLM Summary</span>
                          <textarea
                            id="edit-summary-text"
                            value={editSummaryText}
                            onChange={(e) => setEditSummaryText(e.target.value)}
                            className="detail-input detail-textarea"
                            rows={8}
                            placeholder="Add or edit the project summary"
                          />
                        </label>

                        {editError ? <p className="error-text">{editError}</p> : null}

                        <div className="project-hero-actions">
                          <button
                            type="button"
                            className="hero-action-button save-action-button"
                            onClick={handleSaveProject}
                            disabled={isSavingProject}
                          >
                            {isSavingProject ? 'Saving...' : 'Save Changes'}
                          </button>
                          <button
                            type="button"
                            className="hero-action-button"
                            onClick={handleCancelEdit}
                            disabled={isSavingProject}
                          >
                            Cancel
                          </button>
                        </div>
                      </div>
                    ) : null}

                                        <div className="llm-summary-card">
                      <span className="panel-eyebrow">LLM Summary</span>
                      {selectedProject.llm_summary?.text ? (
                        <>
                          <p>{selectedProject.llm_summary.text}</p>
                          <span className="summary-updated">
                            Updated {formatDate(selectedProject.llm_summary.updated_at)}
                          </span>
                        </>
                      ) : (
                        <p className="empty-copy">No LLM summary saved for this project yet.</p>
                      )}
                    </div>
                  </article>

                  <article className="detail-card">
                    <div className="detail-card-header">
                      <span className="panel-eyebrow">Summary</span>
                      <h4>Quick Read</h4>
                    </div>
                    <div className="metadata-grid">
                      <div className="detail-row">
                        <strong>Contributors</strong>
                        <span>{contributors.length}</span>
                      </div>
                      <div className="detail-row">
                        <strong>Primary Roles</strong>
                        <span>{contributorRoles.length}</span>
                      </div>
                      <div className="detail-row">
                        <strong>Team Composition</strong>
                        <span>{selectedProject.contributor_roles?.summary?.team_composition || 'Not available'}</span>
                      </div>
                    </div>
                  </article>
                </div>
              ) : null}

              {activePanel === 'signals' ? (
                <div className="detail-grid">
                  <article className="detail-card detail-card-wide">
                    <div className="detail-card-header">
                      <span className="panel-eyebrow">File Signals</span>
                      <h4>Extension Breakdown</h4>
                    </div>
                    {extensionEntries.length > 0 ? (
                      <div className="extension-list">
                        {extensionEntries.slice(0, 8).map(([extension, count]) => (
                          <div key={extension || 'none'} className="extension-row">
                            <div className="extension-row-top">
                              <strong>{extension || 'No extension'}</strong>
                              <span>{count} files</span>
                            </div>
                            <div className="extension-bar">
                              <div className="extension-fill" style={{ width: `${(Number(count) / maxExtensionCount) * 100}%` }} />
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="empty-copy">No file extension data available.</p>
                    )}
                  </article>

                  <article className="detail-card">
                    <div className="detail-card-header">
                      <span className="panel-eyebrow">Languages</span>
                      <h4>Detected Stack</h4>
                    </div>
                    {languages.length > 0 ? (
                      <div className="chip-cloud">
                        {languages.map((language) => (
                          <span key={language} className="detail-chip">{language}</span>
                        ))}
                      </div>
                    ) : (
                      <p className="empty-copy">No languages detected.</p>
                    )}
                  </article>

                  <article className="detail-card">
                    <div className="detail-card-header">
                      <span className="panel-eyebrow">Skills</span>
                      <h4>Capability Tags</h4>
                    </div>
                    {skills.length > 0 ? (
                      <div className="chip-cloud">
                        {skills.map((skill) => (
                          <span key={skill} className="detail-chip">{skill}</span>
                        ))}
                      </div>
                    ) : (
                      <p className="empty-copy">No skills recorded.</p>
                    )}
                  </article>
                </div>
              ) : null}

              {activePanel === 'contributors' ? (
                <div className="contributors-panel-stack">
                  <article className="detail-card">
                    <div className="detail-card-header">
                      <span className="panel-eyebrow">People</span>
                      <h4>Contributors</h4>
                    </div>
                    {contributors.length > 0 ? (
                      <div className="chip-cloud">
                        {contributors.map((contributor) => (
                          <span key={contributor} className="detail-chip">{contributor}</span>
                        ))}
                      </div>
                    ) : (
                      <p className="empty-copy">No contributors recorded.</p>
                    )}
                  </article>

                  <article className="detail-card">
                    <div className="detail-card-header">
                      <span className="panel-eyebrow">Roles</span>
                      <h4>Contributor Roles</h4>
                    </div>
                    {contributorRoles.length > 0 ? (
                      <div className="contributors-role-list">
                        {contributorRoles.map((contributor) => (
                          <div key={`${contributor.name}-${contributor.primary_role}`} className="contributor-role-card">
                            <p className="contributor-role-name">{contributor.name}</p>
                            <p className="contributor-role-primary">
                              {contributor.primary_role}
                              {contributor.role_description ? ` - ${contributor.role_description}` : ''}
                            </p>
                            <p className="contributor-role-meta">Confidence: {formatRoleConfidence(contributor.confidence)}</p>
                            {Array.isArray(contributor.secondary_roles) && contributor.secondary_roles.length > 0 ? (
                              <p className="contributor-role-meta">Secondary: {contributor.secondary_roles.join(', ')}</p>
                            ) : null}
                          </div>
                        ))}
                        {selectedProject.contributor_roles?.summary?.team_composition ? (
                          <p className="contributor-role-summary">
                            Team Composition: {selectedProject.contributor_roles.summary.team_composition}
                          </p>
                        ) : null}
                      </div>
                    ) : (
                      <p className="empty-copy">No contributor roles inferred yet.</p>
                    )}
                  </article>
                </div>
              ) : null}

              {activePanel === 'activity' ? (
                <div className="detail-grid">
                  <article className="detail-card detail-card-wide">
                    <div className="detail-card-header">
                      <span className="panel-eyebrow">Timeline</span>
                      <h4>Scan Activity</h4>
                    </div>
                    {scans.length > 0 ? (
                      <div className="activity-list">
                        {scans.map((scan, index) => (
                          <div key={`${scan.id ?? scan.scanned_at ?? index}`} className="activity-item">
                            <span className="activity-dot" aria-hidden="true" />
                            <div>
                              <strong>{formatDate(scan.scanned_at)}</strong>
                              <p>{scan.notes || 'Scan recorded with no additional notes.'}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="empty-copy">No scans have been recorded for this project yet.</p>
                    )}
                  </article>

                  <article className="detail-card">
                    <div className="detail-card-header">
                      <span className="panel-eyebrow">Evidence</span>
                      <h4>Saved Items</h4>
                    </div>
                    {evidence.length > 0 ? (
                      <div className="evidence-list">
                        {evidence.slice(0, 6).map((item, index) => (
                          <div key={`${getEvidenceTitle(item, index)}-${index}`} className="evidence-item">
                            <div className="evidence-item-top">
                              <strong>{getEvidenceTitle(item, index)}</strong>
                              {getEvidenceMeta(item) ? <span className="detail-chip muted">{getEvidenceMeta(item)}</span> : null}
                            </div>
                            <p>{getEvidenceDescription(item) || 'No evidence details available.'}</p>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="empty-copy">No evidence items stored.</p>
                    )}
                  </article>
                </div>
              ) : null}
            </div>
          )}

          {!isLoadingDetails && !detailsError && !selectedProject && projects.length > 0 ? (
            <div className="empty-state-card">
              <h3>Select a project to view details</h3>
              <p>Choose a project from the explorer to open its dashboard.</p>
            </div>
          ) : null}
        </section>
      </div>
    </div>
  );
}

export default ScannedProjectsPage;
