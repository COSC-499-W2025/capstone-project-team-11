import React, { useEffect, useMemo, useState } from 'react';
import axios from 'axios';
import { API_BASE_URL } from './api';

const PHASE_ORDER = [
  'Scanning Files',
  'Detecting Languages & Frameworks',
  'Detecting Skills',
  'Analyzing Project',
  'Generating LLM Summary',
  'Scan Complete!',
];

function normalizeContributorInput(value) {
  return value
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean);
}

function ScanPage({ onBack }) {
  const [scanPath, setScanPath] = useState('');
  const [isScanning, setIsScanning] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [llmSummary, setLlmSummary] = useState(false);
  const [recentProjects, setRecentProjects] = useState([]);
  const [scanNotice, setScanNotice] = useState('');
  const [scanSummary, setScanSummary] = useState(null);
  const [scanPhase, setScanPhase] = useState('');
  const [detectedProjects, setDetectedProjects] = useState([]);
  const [currentProject, setCurrentProject] = useState(null);
  const [currentProjectIndex, setCurrentProjectIndex] = useState(0);
  const [totalProjects, setTotalProjects] = useState(0);
  const [projectResults, setProjectResults] = useState([]);
  const [failedProjects, setFailedProjects] = useState([]);
  const [llmConsentGranted, setLlmConsentGranted] = useState(false);
  const [existingContributors, setExistingContributors] = useState([]);
  const [assignmentQueue, setAssignmentQueue] = useState([]);
  const [assignmentIndex, setAssignmentIndex] = useState(0);
  const [manualAssignments, setManualAssignments] = useState({});
  const [selectedExistingContributor, setSelectedExistingContributor] = useState('');
  const [newContributorNames, setNewContributorNames] = useState('');

  const assignmentProject = assignmentQueue[assignmentIndex] || null;
  const phaseIndex = scanPhase ? Math.max(0, PHASE_ORDER.indexOf(scanPhase)) : 0;
  const perProjectProgress = scanPhase ? Math.round((phaseIndex / (PHASE_ORDER.length - 1)) * 100) : 0;
  const projectProgress = totalProjects > 0 ? ((Math.max(currentProjectIndex, 1) - 1) / totalProjects) * 100 : 0;
  const progressValue =
    totalProjects > 0 ? Math.round(projectProgress + perProjectProgress / Math.max(totalProjects, 1)) : perProjectProgress;
  const showSummary = !isScanning && Array.isArray(scanSummary) && scanSummary.length > 0;
  const assignmentSelectionCount =
    (selectedExistingContributor ? 1 : 0) + normalizeContributorInput(newContributorNames).length;

  const assignmentTitle = useMemo(() => {
    if (!assignmentProject) {
      return '';
    }
    return `Assign contributors for ${assignmentProject.project_name}`;
  }, [assignmentProject]);

  const fetchRecentProjects = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/projects`);
      setRecentProjects(res.data || []);
    } catch {
      setRecentProjects([]);
    }
  };

  useEffect(() => {
    fetchRecentProjects();
    fetch(`${API_BASE_URL}/config`)
      .then((r) => r.ok ? r.json() : Promise.reject())
      .then((cfg) => setLlmConsentGranted(Boolean(cfg.llm_summary_consent)))
      .catch(() => setLlmConsentGranted(false));
  }, []);

  const resetScanState = () => {
    setScanSummary(null);
    setScanPhase('');
    setDetectedProjects([]);
    setCurrentProject(null);
    setCurrentProjectIndex(0);
    setTotalProjects(0);
    setProjectResults([]);
    setFailedProjects([]);
    setAssignmentQueue([]);
    setAssignmentIndex(0);
    setManualAssignments({});
    setSelectedExistingContributor('');
    setNewContributorNames('');
  };

  const updatePhaseFromLine = (line) => {
    const candidates = [...PHASE_ORDER, 'All Scans Complete!'];
    const match = candidates.find((label) => line.includes(label));
    if (!match) {
      return;
    }
    setScanPhase(match === 'All Scans Complete!' ? 'Scan Complete!' : match);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setIsDragging(false);
    const file = event.dataTransfer.files?.[0];
    if (file && file.path) {
      setScanPath(file.path);
      setScanNotice('');
    }
  };

  const handleBrowse = async () => {
    if (!window.api?.openProjectDialog) {
      setScanNotice('File picker unavailable in this build.');
      return;
    }
    const selected = await window.api.openProjectDialog();
    if (selected) {
      setScanPath(selected);
      setScanNotice('');
    }
  };

  const beginStreamingScan = async (contributorsByPath) => {
    setIsScanning(true);
    setScanNotice('');
    setScanPhase('Scanning Files');

    try {
      const response = await fetch(`${API_BASE_URL}/projects/scan-stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_path: scanPath,
          llm_summary: llmSummary,
          manual_contributors_by_path: contributorsByPath,
        }),
      });

      if (!response.ok || !response.body) {
        const msg = await response.text();
        setScanNotice(msg || response.statusText || 'Scan request failed.');
        setIsScanning(false);
        return;
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) {
          break;
        }
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        lines.forEach((line) => {
          if (line.startsWith('SCAN_EVENT::')) {
            try {
              const event = JSON.parse(line.replace('SCAN_EVENT::', '').trim());
              if (event.type === 'projects_detected') {
                setDetectedProjects(event.projects || []);
                setTotalProjects(event.total_projects || 0);
              } else if (event.type === 'scan_phase') {
                setScanPhase(event.phase || 'Scanning Files');
              } else if (event.type === 'project_started') {
                setCurrentProject(event.project_name || null);
                setCurrentProjectIndex(event.project_index || 0);
                setTotalProjects(event.total_projects || totalProjects);
              } else if (event.type === 'project_phase') {
                setCurrentProject(event.project_name || null);
                setScanPhase(event.phase || '');
              } else if (event.type === 'project_completed') {
                setProjectResults((prev) => [
                  ...prev.filter((item) => item.project_path !== event.project_path),
                  { ...event, success: true },
                ]);
              } else if (event.type === 'project_failed') {
                const failure = {
                  project_name: event.project_name,
                  project_path: event.project_path,
                  error: event.error,
                };
                setFailedProjects((prev) => [...prev.filter((item) => item.project_path !== event.project_path), failure]);
                setProjectResults((prev) => [
                  ...prev.filter((item) => item.project_path !== event.project_path),
                  { ...failure, success: false },
                ]);
              }
            } catch {
              setScanNotice('Received malformed scan progress event.');
            }
            return;
          }

          if (line.startsWith('SCAN_DONE::')) {
            try {
              const payload = JSON.parse(line.replace('SCAN_DONE::', '').trim());
              if (payload?.summaries) {
                setScanSummary(payload.summaries);
              }
              if (Array.isArray(payload?.project_results)) {
                setProjectResults(payload.project_results);
              }
              if (Array.isArray(payload?.failed_projects)) {
                setFailedProjects(payload.failed_projects);
              }
              if (payload?.partial_success) {
                setScanNotice('Scan finished with partial success.');
              } else if (payload?.error) {
                setScanNotice(`Scan finished with error: ${payload.error}`);
              } else {
                setScanNotice('');
              }
            } catch {
              setScanNotice('Scan finished.');
            }
            setScanPhase('Scan Complete!');
          } else {
            updatePhaseFromLine(line);
          }
        });
      }

      if (buffer) {
        updatePhaseFromLine(buffer);
      }
      await fetchRecentProjects();
    } catch (err) {
      setScanNotice(`Error: ${err.message}`);
    } finally {
      setIsScanning(false);
    }
  };

  const startScan = async () => {
    if (!scanPath) {
      setScanNotice('Select a project folder or zip file to scan.');
      return;
    }

    resetScanState();
    setScanNotice('');

    try {
      const planResponse = await axios.post(`${API_BASE_URL}/projects/scan-plan`, {
        project_path: scanPath,
        llm_summary: llmSummary,
      });

      const plan = planResponse.data || {};
      const projects = Array.isArray(plan.projects) ? plan.projects : [];
      const nonGitProjects = projects.filter((project) => project.requires_contributor_assignment);

      setDetectedProjects(projects);
      setTotalProjects(plan.total_projects || projects.length);
      setExistingContributors(Array.isArray(plan.existing_contributors) ? plan.existing_contributors : []);

      if (nonGitProjects.length > 0) {
        setAssignmentQueue(nonGitProjects);
        setAssignmentIndex(0);
        return;
      }

      await beginStreamingScan({});
    } catch (err) {
      const message = err?.response?.data?.detail || err.message;
      setScanNotice(`Failed to prepare scan: ${message}`);
    }
  };

  const handleAssignmentSubmit = async () => {
    if (!assignmentProject) {
      return;
    }

    const newNames = normalizeContributorInput(newContributorNames);
    const combined = [...(selectedExistingContributor ? [selectedExistingContributor] : []), ...newNames];
    const deduped = [...new Set(combined)];

    if (deduped.length === 0) {
      setScanNotice('Select one contributor from the dropdown or enter one new contributor name.');
      return;
    }

    if (deduped.length > 1) {
      setScanNotice('Non-git projects can only be assigned to one contributor.');
      return;
    }

    const nextAssignments = {
      ...manualAssignments,
      [assignmentProject.project_path]: deduped,
    };

    setManualAssignments(nextAssignments);
    setSelectedExistingContributor('');
    setNewContributorNames('');
    setScanNotice('');

    if (assignmentIndex + 1 < assignmentQueue.length) {
      setAssignmentIndex((prev) => prev + 1);
      return;
    }

    setAssignmentQueue([]);
    setAssignmentIndex(0);
    await beginStreamingScan(nextAssignments);
  };

  return (
    <div className="page-shell scan-page">
      <header className="app-header">
        <h1>Scan Project</h1>
        <p>Import a local folder or zip and follow the scan progress in real time.</p>
      </header>

      <div className="scan-layout">
        <section className="scan-panel">
          <div
            className={`scan-dropzone ${isDragging ? 'is-dragging' : ''}`}
            onDragOver={(event) => {
              event.preventDefault();
              setIsDragging(true);
            }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
          >
            <p>Drag and drop a project folder or .zip</p>
            <p className="scan-path">{scanPath || 'No project selected yet.'}</p>
            <button type="button" className="secondary" onClick={handleBrowse}>
              Choose Folder or Zip
            </button>
          </div>

          <div className="scan-controls">
            <label
              className="toggle-row"
              onClick={(event) => {
                if (!llmConsentGranted) {
                  event.preventDefault();
                }
              }}
              style={{ cursor: llmConsentGranted ? 'pointer' : 'help' }}
            >
              <input
                type="checkbox"
                checked={llmConsentGranted ? llmSummary : false}
                disabled={!llmConsentGranted}
                onChange={(event) => setLlmSummary(event.target.checked)}
                style={{ cursor: llmConsentGranted ? 'pointer' : 'not-allowed' }}
              />
              <span>
                Generate LLM project summary
                {!llmConsentGranted && (
                  <span style={{ marginLeft: '0.4em', color: 'rgba(251, 255, 0, 0.7)', fontSize: '0.85em' }}>
                    <br></br> Enable LLM resume consent in Privacy Settings to use this.
                  </span>
                )}
              </span>
            </label>

            <div className="scan-actions">
              <button type="button" onClick={startScan} disabled={isScanning || assignmentQueue.length > 0}>
                {isScanning ? 'Scanning...' : 'Start Scan'}
              </button>
              <button type="button" className="secondary" onClick={onBack} disabled={isScanning}>
                Back to Main Menu
              </button>
            </div>

            {scanNotice && <p className="scan-notice">{scanNotice}</p>}
          </div>
        </section>

        {isScanning && !assignmentProject && (
          <section className="scan-log-panel">
            <h2>Scan Progress</h2>
            <div className="scan-progress">
              <div className="progress-track" aria-hidden="true">
                <div className="progress-fill" style={{ width: `${progressValue}%` }} />
              </div>
              <div className="progress-meta">
                <span>{scanPhase || 'Waiting to start scan'}</span>
                <span>{progressValue}%</span>
              </div>
            </div>

            {totalProjects > 0 && (
              <div className="detail-row">
                <strong>Projects Detected:</strong> {totalProjects}
              </div>
            )}

            {currentProject && totalProjects > 0 && (
              <>
                <div className="detail-row">
                  <strong>Current Project:</strong> {currentProject}
                </div>
                <div className="detail-row">
                  <strong>Project Position:</strong> Project {currentProjectIndex} of {totalProjects}
                </div>
              </>
            )}

            {detectedProjects.length > 0 && (
              <div className="summary-list">
                {detectedProjects.map((project) => {
                  const result = projectResults.find((item) => item.project_path === project.project_path);
                  return (
                    <article key={project.project_path} className="summary-card">
                      <h3>{project.project_name}</h3>
                      <p className="summary-path">{project.project_path}</p>
                      <p className="summary-meta">{project.is_git ? 'Git project' : 'Non-git project'}</p>
                      <p className="summary-meta">
                        {result
                          ? result.success
                            ? 'Status: Scanned'
                            : `Status: Failed (${result.error || 'Unknown error'})`
                          : 'Status: Pending'}
                      </p>
                    </article>
                  );
                })}
              </div>
            )}
          </section>
        )}

        {!isScanning && assignmentProject && (
          <section className="scan-log-panel">
            <h2>{assignmentTitle}</h2>
            <p>
              Non-git project detected. Select existing contributors, enter new names, or do both before the scan
              continues.
            </p>
            <div className="detail-row">
              <strong>Project Position:</strong> Assignment {assignmentIndex + 1} of {assignmentQueue.length}
            </div>
            <div className="detail-row">
              <strong>Project Path:</strong> {assignmentProject.project_path}
            </div>

            {existingContributors.length > 0 ? (
              <div style={{ marginTop: '1rem' }}>
                <label style={{ display: 'block' }}>
                  <strong>Existing Contributors</strong>
                  <select
                    value={selectedExistingContributor}
                    onChange={(event) => setSelectedExistingContributor(event.target.value)}
                    style={{ display: 'block', width: '100%', marginTop: '0.5rem' }}
                  >
                    <option value="">Select a contributor</option>
                    {existingContributors.map((name) => (
                      <option key={name} value={name}>
                        {name}
                      </option>
                    ))}
                  </select>
                </label>
                <p className="summary-meta">Choose one existing contributor for this non-git project.</p>
              </div>
            ) : (
              <p className="summary-meta">No existing contributors found in the database yet.</p>
            )}

            <label style={{ display: 'block', marginTop: '1rem' }}>
              <strong>New Contributors</strong>
              <input
                type="text"
                value={newContributorNames}
                onChange={(event) => setNewContributorNames(event.target.value)}
                placeholder="Or enter one new contributor name"
                style={{ display: 'block', width: '100%', marginTop: '0.5rem' }}
              />
            </label>

            <div className="detail-row" style={{ marginTop: '1rem' }}>
              <strong>Selected Contributors:</strong> {assignmentSelectionCount}
            </div>

            <div className="scan-actions" style={{ marginTop: '1rem' }}>
              <button type="button" onClick={handleAssignmentSubmit}>
                Save Contributors
              </button>
              <button type="button" className="secondary" onClick={() => setAssignmentQueue([])} disabled={isScanning}>
                Cancel Scan
              </button>
            </div>
          </section>
        )}

        {!isScanning && !assignmentProject && showSummary ? (
          <section className="scan-log-panel">
            <h2>Project Summary</h2>
            {failedProjects.length > 0 && (
              <p className="scan-notice">
                {failedProjects.length} project{failedProjects.length === 1 ? '' : 's'} failed during the scan.
              </p>
            )}
            <div className="summary-list">
              {scanSummary.map((summary, index) => (
                <article key={`${summary.project_name || index}`} className="summary-card">
                  <h3>{summary.project_name || 'Project'}</h3>
                  {summary.project_path && <p className="summary-path">{summary.project_path}</p>}
                  {summary.generated_at && <p className="summary-meta">Generated: {summary.generated_at}</p>}
                  {Array.isArray(summary.high_confidence_languages) &&
                    summary.high_confidence_languages.length > 0 && (
                      <p>
                        <strong>Languages:</strong> {summary.high_confidence_languages.join(', ')}
                      </p>
                    )}
                  {Array.isArray(summary.high_confidence_frameworks) &&
                    summary.high_confidence_frameworks.length > 0 && (
                      <p>
                        <strong>Frameworks:</strong> {summary.high_confidence_frameworks.join(', ')}
                      </p>
                    )}
                  {Array.isArray(summary.high_confidence_skills) &&
                    summary.high_confidence_skills.length > 0 && (
                      <p>
                        <strong>Skills:</strong> {summary.high_confidence_skills.join(', ')}
                      </p>
                    )}
                  {summary.llm_summary?.text && (
                    <div className="summary-llm">
                      <h4>LLM Summary</h4>
                      <p>{summary.llm_summary.text}</p>
                      {summary.llm_summary.updated_at && (
                        <p className="summary-meta">Updated: {summary.llm_summary.updated_at}</p>
                      )}
                    </div>
                  )}
                </article>
              ))}
            </div>
          </section>
        ) : null}

        {!isScanning && recentProjects.length > 0 ? (
          <section className="scan-log-panel">
            <h2>Recent Saved Projects</h2>
            <div className="summary-list">
              {recentProjects.slice(-4).reverse().map((project) => (
                <article key={project.id} className="summary-card">
                  <h3>{project.name}</h3>
                  {project.latest_scan_at && <p className="summary-meta">Last Scan: {project.latest_scan_at}</p>}
                </article>
              ))}
            </div>
          </section>
        ) : null}
      </div>
    </div>
  );
}

export default ScanPage;
