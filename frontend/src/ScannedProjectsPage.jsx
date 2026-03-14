import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { API_BASE_URL } from './api';

function ScannedProjectsPage({ onBack }) {
  const [projects, setProjects] = useState([]);
  const [selectedProjectId, setSelectedProjectId] = useState(null);
  const [selectedProject, setSelectedProject] = useState(null);
  const [isLoadingProjects, setIsLoadingProjects] = useState(true);
  const [isLoadingDetails, setIsLoadingDetails] = useState(false);
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

              <div style={{ margin: '0.75rem 0 1rem' }}>
                <button
                  type="button"
                  onClick={handleEditProject}
                  style={{
                    background: '#3b82f6',
                    border: 'none',
                    color: 'white',
                    padding: '0.45rem 0.75rem',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '0.8rem',
                    fontWeight: 600,
                    marginRight: '0.5rem',
                  }}
                >
                  Edit Project
                </button>

                <button
                  type="button"
                  onClick={handleDeleteProject}
                  style={{
                    background: '#ef4444',
                    border: 'none',
                    color: 'white',
                    padding: '0.45rem 0.75rem',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '0.8rem',
                    fontWeight: 600,
                  }}
                >
                  Delete Project
                </button>
              </div>

              <div className="detail-row">
                <strong>Project ID:</strong> {selectedProject.project?.id ?? selectedProjectId}
              </div>

              {selectedProject.project?.created_at && (
                <div className="detail-row">
                  <strong>Created At:</strong> {selectedProject.project.created_at}
                </div>
              )}

              {selectedProject.project?.repo_url && (
                <div className="detail-row">
                  <strong>Repo URL:</strong> {selectedProject.project.repo_url}
                </div>
              )}

              {selectedProject.project?.thumbnail_path && (
                <div className="detail-row">
                  <strong>Thumbnail Path:</strong> {selectedProject.project.thumbnail_path}
                </div>
              )}

              {isEditing && (
                <div style={{ marginTop: '1rem', marginBottom: '1rem' }}>
                  <h4>Edit Project Info</h4>

                  <div className="detail-row" style={{ marginTop: '0.5rem' }}>
                    <strong>Display Name:</strong>
                    <input
                      type="text"
                      value={editCustomName}
                      onChange={(e) => setEditCustomName(e.target.value)}
                      style={{ marginLeft: '0.5rem', padding: '0.35rem' }}
                    />
                  </div>

                  <div className="detail-row" style={{ marginTop: '0.5rem' }}>
                    <strong>Repo URL:</strong>
                    <input
                      type="text"
                      value={editRepoUrl}
                      onChange={(e) => setEditRepoUrl(e.target.value)}
                      style={{ marginLeft: '0.5rem', padding: '0.35rem', width: '60%' }}
                    />
                  </div>

                  <div className="detail-row" style={{ marginTop: '0.5rem' }}>
                    <strong>Thumbnail Path:</strong>
                    <input
                      type="text"
                      value={editThumbnailPath}
                      onChange={(e) => setEditThumbnailPath(e.target.value)}
                      style={{ marginLeft: '0.5rem', padding: '0.35rem', width: '60%' }}
                    />
                  </div>

                  <div style={{ marginTop: '0.75rem' }}>
                    <button
                      type="button"
                      onClick={handleSaveProject}
                      style={{
                        background: '#10b981',
                        border: 'none',
                        color: 'white',
                        padding: '0.45rem 0.75rem',
                        borderRadius: '6px',
                        cursor: 'pointer',
                        fontSize: '0.8rem',
                        fontWeight: 600,
                        marginRight: '0.5rem',
                      }}
                    >
                      Save Changes
                    </button>

                    <button
                      type="button"
                      onClick={() => setIsEditing(false)}
                      style={{
                        background: '#6b7280',
                        border: 'none',
                        color: 'white',
                        padding: '0.45rem 0.75rem',
                        borderRadius: '6px',
                        cursor: 'pointer',
                        fontSize: '0.8rem',
                        fontWeight: 600,
                      }}
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}

              {Array.isArray(selectedProject.languages) && selectedProject.languages.length > 0 && (
                <div className="detail-row">
                  <strong>Languages:</strong> {selectedProject.languages.join(', ')}
                </div>
              )}

              {Array.isArray(selectedProject.skills) && selectedProject.skills.length > 0 && (
                <div className="detail-row">
                  <strong>Skills:</strong> {selectedProject.skills.join(', ')}
                </div>
              )}

              {Array.isArray(selectedProject.contributors) &&
                selectedProject.contributors.length > 0 && (
                  <div className="detail-row">
                    <strong>Contributors:</strong> {selectedProject.contributors.join(', ')}
                  </div>
                )}

              {selectedProject.llm_summary?.text && (
                <div style={{ marginTop: '1rem' }}>
                  <strong>LLM Summary:</strong>
                  <p style={{ marginTop: '0.35rem' }}>{selectedProject.llm_summary.text}</p>

                  {selectedProject.llm_summary?.model && (
                    <p style={{ marginTop: '0.35rem' }}>
                      <strong>Model:</strong> {selectedProject.llm_summary.model}
                    </p>
                  )}

                  {selectedProject.llm_summary?.updated_at && (
                    <p style={{ marginTop: '0.35rem' }}>
                      <strong>Updated At:</strong> {selectedProject.llm_summary.updated_at}
                    </p>
                  )}
                </div>
              )}

              {selectedProject.files_summary?.total_files != null && (
                <div className="detail-row">
                  <strong>Total Files:</strong> {selectedProject.files_summary.total_files}
                </div>
              )}

              {selectedProject.files_summary?.extensions &&
                Object.keys(selectedProject.files_summary.extensions).length > 0 && (
                  <div className="detail-row">
                    <strong>Extensions:</strong>{' '}
                    {Object.entries(selectedProject.files_summary.extensions)
                      .map(([ext, count]) => `${ext}: ${count}`)
                      .join(', ')}
                  </div>
                )}

              {Array.isArray(selectedProject.scans) && selectedProject.scans.length > 0 && (
                <div className="detail-row">
                  <strong>Latest Scan:</strong> {selectedProject.scans[0].scanned_at}
                </div>
              )}

              {Array.isArray(selectedProject.evidence) && (
                <div className="detail-row">
                  <strong>Evidence Items:</strong> {selectedProject.evidence.length}
                </div>
              )}
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