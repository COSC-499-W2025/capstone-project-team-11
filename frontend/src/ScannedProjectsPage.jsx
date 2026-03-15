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

function formatRoleConfidence(value) {
  if (typeof value !== 'number' || Number.isNaN(value)) {
    return '0%';
  }
  return `${Math.round(value * 100)}%`;
}

function DetailRow({ label, children }) {
  return (
    <div className="detail-row detail-row-grid">
      <span className="detail-label">{label}</span>
      <span className="detail-value">{children}</span>
    </div>
  );
}

function PillList({ items, emptyText = 'None' }) {
  if (!Array.isArray(items) || items.length === 0) {
    return <span className="detail-empty">{emptyText}</span>;
  }

  return (
    <span className="pill-list">
      {items.map((item) => (
        <span key={item} className="text-pill">
          {item}
        </span>
      ))}
    </span>
  );
}

function ScannedProjectsPage({ onBack }) {
  const [projects, setProjects] = useState([]);
  const [selectedProjectId, setSelectedProjectId] = useState(null);
  const [selectedProject, setSelectedProject] = useState(null);
  const [isLoadingProjects, setIsLoadingProjects] = useState(true);
  const [isLoadingDetails, setIsLoadingDetails] = useState(false);
  const [isUpdatingThumbnail, setIsUpdatingThumbnail] = useState(false);
  const [projectsError, setProjectsError] = useState('');
  const [detailsError, setDetailsError] = useState('');

  const [isEditing, setIsEditing] = useState(false);
  const [editCustomName, setEditCustomName] = useState('');
  const [editRepoUrl, setEditRepoUrl] = useState('');
  const [editThumbnailPath, setEditThumbnailPath] = useState('');

  useEffect(() => {
    const loadProjects = async () => {
      setIsLoadingProjects(true);
      setProjectsError('');

      try {
        const response = await axios.get(`${API_BASE_URL}/projects`);
        const projectList = Array.isArray(response.data) ? response.data : [];

        setProjects(projectList);

        if (projectList.length > 0) {
          const firstProjectId = projectList[0].project_id ?? projectList[0].id;
          setSelectedProjectId(firstProjectId);
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
    }
  }, [selectedProject, isEditing]);

  const handleEditProject = () => {
    if (!selectedProject) {
      return;
    }

    setEditCustomName(selectedProject.project?.custom_name || '');
    setEditRepoUrl(selectedProject.project?.repo_url || '');
    setEditThumbnailPath(selectedProject.project?.thumbnail_path || '');
    setIsEditing(true);
  };

  const handleSaveProject = async () => {
    if (selectedProjectId == null) {
      return;
    }

    try {
      await axios.patch(`${API_BASE_URL}/projects/${selectedProjectId}`, {
        custom_name: editCustomName,
        repo_url: editRepoUrl,
        thumbnail_path: editThumbnailPath,
      });

      alert('Project updated successfully');
      setIsEditing(false);

      const detailsResponse = await axios.get(`${API_BASE_URL}/projects/${selectedProjectId}`);
      setSelectedProject(detailsResponse.data);

      const listResponse = await axios.get(`${API_BASE_URL}/projects`);
      setProjects(Array.isArray(listResponse.data) ? listResponse.data : []);
    } catch (error) {
      console.error('Failed to update project:', error);
      alert('Failed to update project.');
    }
  };

  const handleDeleteProject = async () => {
  if (selectedProjectId == null) {
    return;
  }

  const projectName =
    selectedProject?.project?.custom_name ||
    selectedProject?.project?.name ||
    `Project ${selectedProjectId}`;

  const confirmed = window.confirm(
    `Are you sure you want to delete "${projectName}"?`
  );

    if (!confirmed) {
      return;
    }

    try {
      await axios.delete(`${API_BASE_URL}/projects/${selectedProjectId}`);
      alert('Project deleted successfully');

      const updatedProjects = projects.filter((project) => {
        const projectId = project.project_id ?? project.id;
        return projectId !== selectedProjectId;
      });

      setProjects(updatedProjects);
      setIsEditing(false);

      if (updatedProjects.length > 0) {
        const nextId = updatedProjects[0].project_id ?? updatedProjects[0].id;
        setSelectedProjectId(nextId);
      } else {
        setSelectedProjectId(null);
        setSelectedProject(null);
      }
    } catch (error) {
      console.error('Failed to delete project:', error);
      alert('Failed to delete project.');
    }
  };

  const handleUpdateThumbnail = async () => {
    if (selectedProjectId == null || !selectedProject?.project) {
      return;
    }

    const nextThumbnailPath = await window.api?.openThumbnailDialog?.();
    if (!nextThumbnailPath) {
      return;
    }

    try {
      setIsUpdatingThumbnail(true);
      await axios.patch(`${API_BASE_URL}/projects/${selectedProjectId}`, {
        thumbnail_path: nextThumbnailPath,
      });

      if (isEditing) {
        setEditThumbnailPath(nextThumbnailPath);
      }

      const detailsResponse = await axios.get(`${API_BASE_URL}/projects/${selectedProjectId}`);
      setSelectedProject(detailsResponse.data);

      const listResponse = await axios.get(`${API_BASE_URL}/projects`);
      setProjects(Array.isArray(listResponse.data) ? listResponse.data : []);
    } catch (error) {
      console.error('Failed to update project thumbnail:', error);
      alert('Failed to update project thumbnail.');
    } finally {
      setIsUpdatingThumbnail(false);
    }
  };

  const thumbnailSrc = getThumbnailSrc(
    selectedProjectId,
    selectedProject?.project?.thumbnail_path
  );

  return (
    <div className="page-shell scanned-projects-page">
      <header className="app-header">
        <h1>Scanned Projects</h1>
        <p>Browse previously scanned projects and inspect saved project details.</p>
      </header>

      <div className="scanned-projects-toolbar">
        <button type="button" className="secondary" onClick={onBack}>
          Back to Main Menu
        </button>
      </div>

      <div className="scanned-projects-layout">
        <aside className="projects-list-panel">
          <h2>Project List</h2>

          {isLoadingProjects && <p>Loading projects...</p>}
          {projectsError && <p className="error-text">{projectsError}</p>}

          {!isLoadingProjects && !projectsError && projects.length === 0 && (
            <div className="empty-state-card">
              <h3>No scanned projects yet</h3>
              <p>Scan a project first to see it here.</p>
            </div>
          )}

          {!isLoadingProjects && !projectsError && projects.length > 0 && (
            <div className="projects-list">
              {projects.map((project) => {
                const projectId = project.project_id ?? project.id;
                const projectName =
                  project.custom_name ??
                  project.display_name ??
                  project.name ??
                  project.project_name ??
                  `Project ${projectId}`;

                return (
                  <button
                    key={projectId}
                    type="button"
                    className={`project-list-item ${
                      selectedProjectId === projectId ? 'is-selected' : ''
                    }`}
                    onClick={() => setSelectedProjectId(projectId)}
                  >
                    <span className="project-list-title">{projectName}</span>
                    <span className="project-list-subtitle">ID: {projectId}</span>
                  </button>
                );
              })}
            </div>
          )}
        </aside>

        <section className="project-details-panel">
          <h2>Project Details</h2>

          {isLoadingDetails && <p>Loading project details...</p>}
          {detailsError && <p className="error-text">{detailsError}</p>}

          {!isLoadingDetails && !detailsError && selectedProject && (
            <div className="project-details-card">
              <h3>
                {selectedProject.project?.custom_name ||
                  selectedProject.project?.name ||
                  `Project ${selectedProjectId}`}
              </h3>

              <div className="project-actions-row">
                <button
                  type="button"
                  className="project-action-btn project-action-btn-edit"
                  onClick={handleEditProject}
                >
                  Edit Project
                </button>

                <button
                  type="button"
                  className="project-action-btn project-action-btn-delete"
                  onClick={handleDeleteProject}
                >
                  Delete Project
                </button>

                <button
                  type="button"
                  className="project-action-btn project-action-btn-thumbnail"
                  onClick={handleUpdateThumbnail}
                  disabled={isUpdatingThumbnail}
                >
                  {isUpdatingThumbnail
                    ? 'Saving Thumbnail...'
                    : (selectedProject.project?.thumbnail_path ? 'Change Thumbnail' : 'Add Thumbnail')}
                </button>
              </div>

              <section className="details-section">
                <h4 className="details-section-title">Overview</h4>

                <DetailRow label="Project ID">{selectedProject.project?.id ?? selectedProjectId}</DetailRow>

                {selectedProject.project?.created_at && (
                  <DetailRow label="Created At">{selectedProject.project.created_at}</DetailRow>
                )}

                {selectedProject.project?.repo_url && (
                  <DetailRow label="Repo URL">{selectedProject.project.repo_url}</DetailRow>
                )}

                {selectedProject.project?.thumbnail_path && (
                  <DetailRow label="Thumbnail Path">{selectedProject.project.thumbnail_path}</DetailRow>
                )}

                {selectedProject.project?.thumbnail_path && (
                  <div className="project-thumbnail-preview">
                    <img
                      src={thumbnailSrc}
                      alt={`${
                        selectedProject.project?.custom_name ||
                        selectedProject.project?.name ||
                        `Project ${selectedProjectId}`
                      } thumbnail`}
                      className="project-thumbnail-image"
                    />
                  </div>
                )}

                {Array.isArray(selectedProject.scans) && selectedProject.scans.length > 0 && (
                  <DetailRow label="Latest Scan">{selectedProject.scans[0].scanned_at}</DetailRow>
                )}
              </section>

              {isEditing && (
                <section className="details-section details-section-edit">
                  <h4 className="details-section-title">Edit Project Info</h4>

                  <div className="detail-row detail-row-grid detail-row-edit">
                    <label className="detail-label" htmlFor="edit-custom-name">
                      Display Name
                    </label>
                    <input
                      id="edit-custom-name"
                      type="text"
                      value={editCustomName}
                      onChange={(e) => setEditCustomName(e.target.value)}
                      className="detail-input"
                    />
                  </div>

                  <div className="detail-row detail-row-grid detail-row-edit">
                    <label className="detail-label" htmlFor="edit-repo-url">
                      Repo URL
                    </label>
                    <input
                      id="edit-repo-url"
                      type="text"
                      value={editRepoUrl}
                      onChange={(e) => setEditRepoUrl(e.target.value)}
                      className="detail-input"
                    />
                  </div>

                  <div className="detail-row detail-row-grid detail-row-edit">
                    <label className="detail-label" htmlFor="edit-thumbnail-path">
                      Thumbnail Path
                    </label>
                    <input
                      id="edit-thumbnail-path"
                      type="text"
                      value={editThumbnailPath}
                      onChange={(e) => setEditThumbnailPath(e.target.value)}
                      className="detail-input"
                    />
                  </div>

                  <div className="project-actions-row">
                    <button
                      type="button"
                      onClick={handleSaveProject}
                      className="project-action-btn project-action-btn-save"
                    >
                      Save Changes
                    </button>

                    <button
                      type="button"
                      onClick={() => setIsEditing(false)}
                      className="project-action-btn project-action-btn-cancel"
                    >
                      Cancel
                    </button>
                  </div>
                </section>
              )}

              <section className="details-section">
                <h4 className="details-section-title">Contributors and Skills</h4>
                <DetailRow label="Languages">
                  <PillList items={selectedProject.languages} emptyText="No languages detected" />
                </DetailRow>
                <DetailRow label="Skills">
                  <PillList items={selectedProject.skills} emptyText="No skills detected" />
                </DetailRow>
                <DetailRow label="Contributors">
                  <PillList items={selectedProject.contributors} emptyText="No contributors found" />
                </DetailRow>
              </section>

              {Array.isArray(selectedProject.contributor_roles?.contributors) &&
                selectedProject.contributor_roles.contributors.length > 0 && (
                  <section className="details-section">
                    <h4 className="details-section-title">Contributor Roles</h4>
                    <div className="contributors-role-list">
                      {selectedProject.contributor_roles.contributors.map((contributor) => (
                        <div
                          key={`${contributor.name}-${contributor.primary_role}`}
                          className="contributor-role-card"
                        >
                          <p className="contributor-role-name">{contributor.name}</p>
                          <p className="contributor-role-primary">
                            {contributor.primary_role}
                            {contributor.role_description ? ` - ${contributor.role_description}` : ''}
                          </p>
                          <p className="contributor-role-meta">
                            Confidence: {formatRoleConfidence(contributor.confidence)}
                          </p>
                          {Array.isArray(contributor.secondary_roles) &&
                            contributor.secondary_roles.length > 0 && (
                              <p className="contributor-role-meta">
                                Secondary: {contributor.secondary_roles.join(', ')}
                              </p>
                            )}
                        </div>
                      ))}
                    </div>
                    {selectedProject.contributor_roles.summary?.team_composition && (
                      <p className="contributor-role-summary">
                        Team Composition: {selectedProject.contributor_roles.summary.team_composition}
                      </p>
                    )}
                  </section>
                )}

              {selectedProject.llm_summary?.text && (
                <section className="details-section">
                  <h4 className="details-section-title">LLM Summary</h4>
                  <p className="llm-summary-text">{selectedProject.llm_summary.text}</p>

                  {selectedProject.llm_summary?.model && (
                    <DetailRow label="Model">{selectedProject.llm_summary.model}</DetailRow>
                  )}

                  {selectedProject.llm_summary?.updated_at && (
                    <DetailRow label="Updated At">{selectedProject.llm_summary.updated_at}</DetailRow>
                  )}
                </section>
              )}

              <section className="details-section">
                <h4 className="details-section-title">Project Stats</h4>
                {selectedProject.files_summary?.total_files != null && (
                  <DetailRow label="Total Files">{selectedProject.files_summary.total_files}</DetailRow>
                )}

                {selectedProject.files_summary?.extensions &&
                  Object.keys(selectedProject.files_summary.extensions).length > 0 && (
                    <DetailRow label="Extensions">
                      <span className="extensions-wrap">
                        {Object.entries(selectedProject.files_summary.extensions).map(([ext, count]) => (
                          <span key={ext || 'none'} className="text-pill text-pill-subtle">
                            {ext || '(no ext)'}: {count}
                          </span>
                        ))}
                      </span>
                    </DetailRow>
                  )}

                {Array.isArray(selectedProject.evidence) && (
                  <DetailRow label="Evidence Items">{selectedProject.evidence.length}</DetailRow>
                )}
              </section>
            </div>
          )}

          {!isLoadingDetails && !detailsError && !selectedProject && projects.length > 0 && (
            <p>Select a project to view details.</p>
          )}
        </section>
      </div>
    </div>
  );
}

export default ScannedProjectsPage;
