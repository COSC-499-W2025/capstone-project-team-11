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
      return;
    }

    const loadProjectDetails = async () => {
      setIsLoadingDetails(true);
      setDetailsError('');

      try {
        const response = await axios.get(`${API_BASE_URL}/projects/${selectedProjectId}`)
        setSelectedProject(response.data);
      } catch (err) {
        setDetailsError(`Failed to load project details: ${err.message}`);
      } finally {
        setIsLoadingDetails(false);
      }
    };

    loadProjectDetails();
  }, [selectedProjectId]);

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
              <h3>{selectedProject.project?.name || `Project ${selectedProjectId}`}</h3>

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