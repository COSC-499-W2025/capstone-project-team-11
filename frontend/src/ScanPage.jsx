import React, { useEffect, useState } from 'react';
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

function ScanPage({ onBack }) {
  const [scanPath, setScanPath] = useState('');
  const [isScanning, setIsScanning] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [llmSummary, setLlmSummary] = useState(false);
  const [recentProjects, setRecentProjects] = useState([]);
  const [scanNotice, setScanNotice] = useState('');
  const [scanSummary, setScanSummary] = useState(null);
  const [scanPhase, setScanPhase] = useState('');

  const phaseIndex = scanPhase ? Math.max(0, PHASE_ORDER.indexOf(scanPhase)) : 0;
  const progressValue = scanPhase ? Math.round((phaseIndex / (PHASE_ORDER.length - 1)) * 100) : 0;
  const showSummary = !isScanning && Array.isArray(scanSummary) && scanSummary.length > 0;

  const fetchRecentProjects = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/projects`)
      setRecentProjects(res.data || []);
    } catch {
      setRecentProjects([]);
    }
  };

  useEffect(() => {
    fetchRecentProjects();
  }, []);

  const updatePhaseFromLine = (line) => {
    const candidates = [
      'Scanning Files',
      'Detecting Languages & Frameworks',
      'Detecting Skills',
      'Analyzing Project',
      'Generating LLM Summary',
      'Scan Complete!',
      'All Scans Complete!',
    ];
    const match = candidates.find((label) => line.includes(label));
    if (!match) {
      return;
    }
    if (match === 'All Scans Complete!') {
      setScanPhase('Scan Complete!');
      return;
    }
    setScanPhase(match);
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

  const startScan = async () => {
    if (!scanPath) {
      setScanNotice('Select a project folder or zip file to scan.');
      return;
    }

    setIsScanning(true);
    setScanNotice('');
    setScanSummary(null);
    setScanPhase('Scanning Files');

    try {
      const response = await fetch(`${API_BASE_URL}/projects/scan-stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_path: scanPath,
          llm_summary: llmSummary,
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
          if (line.startsWith('SCAN_DONE::')) {
            try {
              const payload = JSON.parse(line.replace('SCAN_DONE::', '').trim());
              if (payload?.summaries) {
                setScanSummary(payload.summaries);
              }
              if (payload?.error) {
                setScanNotice(`Scan finished with error: ${payload.error}`);
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
            <label className="toggle-row">
              <input
                type="checkbox"
                checked={llmSummary}
                onChange={(event) => setLlmSummary(event.target.checked)}
              />
              <span>Generate LLM project summary</span>
            </label>

            <div className="scan-actions">
              <button type="button" onClick={startScan} disabled={isScanning}>
                {isScanning ? 'Scanning...' : 'Start Scan'}
              </button>
              <button type="button" className="secondary" onClick={onBack} disabled={isScanning}>
                Back to Main Menu
              </button>
            </div>

            {scanNotice && <p className="scan-notice">{scanNotice}</p>}
          </div>
        </section>

        {isScanning ? (
          <section className="scan-log-panel">
            <h2>Scan Progress</h2>
            <div className="scan-progress">
              <div className="progress-track" aria-hidden="true">
                <div className="progress-fill" style={{ width: `${progressValue}%` }} />
              </div>
              <div className="progress-meta">
                <span>{scanPhase || 'Scanning...'}</span>
                <span>{progressValue}%</span>
              </div>
            </div>
          </section>
        ) : null}

        {showSummary ? (
          <section className="scan-log-panel">
            <h2>Project Summary</h2>
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

        <section className="scan-recent">
  <h2>Recent Scans</h2>
  {recentProjects.length === 0 ? (
    <p>No recent scans yet.</p>
  ) : (
    <div className="recent-list">
      {recentProjects.map((project) => {
        const projectId = project.project_id ?? project.id;
        const projectName =
          project.display_name ?? project.name ?? project.project_name ?? `Project ${projectId}`;

        return (
          <div key={projectId} className="recent-item">
            <div className="recent-title">{projectName}</div>
            <div className="recent-meta">
              Last scan: {project.latest_scan_at || 'Not available'}
            </div>
          </div>
        );
      })}
    </div>
  )}
</section>
      </div>
    </div>
  );
}

export default ScanPage;