import React, { useEffect, useRef, useState } from 'react';
import ReactDOM from 'react-dom';
import axios from 'axios';
import { API_BASE_URL } from './api';
import { showModal } from "./modal";

const MAX_FEATURED = 3;

function formatRoleConfidence(value) {
  if (typeof value !== 'number' || Number.isNaN(value)) return '0%';
  return `${Math.round(value * 100)}%`;
}

// Modal component to act as an expanded project card, showing all available information about the project and the user's contributions to it
function ProjectModal({ project, detail, username, displayName, onClose }) {
  const name = project.display_name ?? project.name ?? '(unnamed)';
  const projectId = project.id ?? project.project_id;
  const thumbSrc = getThumbnailSrc(projectId, project.thumbnail_path);
  const languages = Array.isArray(detail?.languages) ? detail.languages : [];
  const frameworks = Array.isArray(detail?.frameworks) ? detail.frameworks : [];
  const skills = Array.isArray(detail?.skills) ? detail.skills : [];
  const contributors = Array.isArray(detail?.contributors) ? detail.contributors : [];
  const evidence = Array.isArray(detail?.evidence) ? detail.evidence : [];
  const filesSummary = detail?.files_summary ?? {};
  const git = detail?.git_metrics ?? {};
  const llmSummary = detail?.llm_summary?.text ?? null;
  const repoUrl = detail?.project?.repo_url ?? null;

  // Filter contributor roles to only the selected portfolio user
  const allRoles = Array.isArray(detail?.contributor_roles?.contributors)
    ? detail.contributor_roles.contributors
    : [];
  const userRole = allRoles.find(
    (c) => c.name?.toLowerCase() === username?.toLowerCase()
  ) ?? null;

  // Git metrics helpers
  const totalCommits = git?.total_commits ?? null;
  const durationDays = git?.duration_days ?? null;
  const projectStart = git?.project_start ? String(git.project_start).slice(0, 10) : null;
  const projectEnd = git?.project_end ? String(git.project_end).slice(0, 10) : null;
  const linesAdded = git?.lines_added_per_author?.[username] ?? null;
  const linesRemoved = git?.lines_removed_per_author?.[username] ?? null;
  const linesAddedPerAuthor = git?.lines_added_per_author ?? {};
  const totalLinesAdded = Object.values(linesAddedPerAuthor).reduce((s, v) => s + (v ?? 0), 0) || null;
  const userCommits = git?.commits_per_author?.[username] ?? null;
  const commitsPerAuthor = git?.commits_per_author ?? {};
  const allAuthors = Object.entries(commitsPerAuthor).sort((a, b) => b[1] - a[1]);
  const userRank = allAuthors.findIndex(([n]) => n.toLowerCase() === username?.toLowerCase());
  const commitPct = totalCommits && userCommits != null ? ((userCommits / totalCommits) * 100).toFixed(1) : null;
  const avgCommitsPerWeek = (durationDays && userCommits != null && durationDays > 0)
    ? (userCommits / Math.max(1, durationDays / 7)).toFixed(1)
    : null;

  // Rank Projects Score
  const rankScore = detail?.rank_score ?? null;

  // Contribution breakdown (from role analysis)
  const breakdown = userRole?.contribution_breakdown ?? null;
  const breakdownEntries = breakdown
    ? Object.entries(breakdown).filter(([, v]) => v > 0).sort((a, b) => b[1] - a[1])
    : [];

  // Top 6 file extensions (skip if empty)
  const extEntries = Object.entries(filesSummary.extensions ?? {})
    .filter(([ext]) => ext)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 6);

  const isCollaborative = contributors.length > 1;

  // Expanded Project Card Modal
  return (
    <div className="modal-overlay" onClick={onClose} role="dialog" aria-modal="true" aria-label={`${name} details`}>
      <div
        className="modal-card"
        style={{ width: '720px', maxWidth: '95vw', maxHeight: '85vh', overflowY: 'auto', background: 'radial-gradient(circle at center, #0a5948, #08271f 80%)', border: '1px solid rgba(74,222,128,0.18)', textAlign: 'left' }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="detail-card-header" style={{ marginBottom: '1rem' }}>
          <div>
            <span className="panel-eyebrow">Project · {isCollaborative ? 'Collaborative' : 'Individual'}</span>
            <h3 style={{ margin: 0 }}>{name}</h3>
            {(projectStart || projectEnd) && (
              <span className="modal-date-range">
                {projectStart ?? '?'} → {projectEnd ?? 'present'}
              </span>
            )}
          </div>
          <button type="button" className="hero-action-button" onClick={onClose}>✕ Close</button>
        </div>

        {/* Thumbnail */}
        {thumbSrc && (
          <div style={{ position: 'relative', width: '100%', aspectRatio: '16/9', marginBottom: '1rem', overflow: 'hidden', border: 'none' }}>
            <img src={thumbSrc} alt={`${name} thumbnail`} style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'contain', background: 'rgba(255,255,255,0)' }} />
          </div>
        )}

        {/* LLM Project Summary */}
        {llmSummary && (
          <div className="modal-section">
            <span className="panel-eyebrow">About</span>
            <p className="modal-section-body">{llmSummary}</p>
          </div>
        )}

        {/* Languages & Frameworks & File Extensions */}
        {(languages.length > 0 || frameworks.length > 0 || extEntries.length > 0) && (
          <div className="detail-grid modal-grid-row">
            {(languages.length > 0 || frameworks.length > 0) && (
              <article className="detail-card">
                <div className="detail-card-header"><span className="panel-eyebrow">Languages &amp; Frameworks</span></div>
                <div className="chip-cloud">
                  {languages.map((lang) => <span key={lang} className="detail-chip">{lang}</span>)}
                  {frameworks.map((fw) => <span key={fw} className="detail-chip">{fw}</span>)}
                </div>
              </article>
            )}
            {extEntries.length > 0 && (
              <article className="detail-card">
                <div className="detail-card-header"><span className="panel-eyebrow">File Breakdown</span></div>
                <div className="chip-cloud">
                  {extEntries.map(([ext, count]) => (
                    <span key={ext} className="detail-chip">
                      {ext}<span className="chip-count">×{count}</span>
                    </span>
                  ))}
                </div>
              </article>
            )}
          </div>
        )}

        {/* Skills */}
        {skills.length > 0 && (
          <article className="detail-card modal-full-row">
            <div className="detail-card-header"><span className="panel-eyebrow">Skills</span></div>
            <div className="chip-cloud">
              {skills.map((skill) => <span key={skill} className="detail-chip">{skill}</span>)}
            </div>
          </article>
        )}

        {/* Project Metrics (Total: Commits, Lines of Code, Files, Days Active) */}
        {(totalCommits != null || totalLinesAdded != null || filesSummary.total_files > 0 || durationDays != null) && (
          <>
            <span className="modal-tiles-heading">Project Metrics</span>
            <div className="modal-metric-tiles">
              {totalCommits != null && (
                <div className="metric-tile">
                  <span className="metric-tile-value">{totalCommits.toLocaleString()}</span>
                  <span className="metric-tile-label">Total Commits</span>
                </div>
              )}
              {totalLinesAdded != null && (
                <div className="metric-tile">
                  <span className="metric-tile-value">{totalLinesAdded.toLocaleString()}</span>
                  <span className="metric-tile-label">Lines of Code</span>
                </div>
              )}
              {filesSummary.total_files > 0 && (
                <div className="metric-tile">
                  <span className="metric-tile-value">{filesSummary.total_files.toLocaleString()}</span>
                  <span className="metric-tile-label">Files</span>
                </div>
              )}
              {durationDays != null && (
                <div className="metric-tile">
                  <span className="metric-tile-value">{durationDays.toLocaleString()}</span>
                  <span className="metric-tile-label">Days Active</span>
                </div>
              )}
            </div>
          </>
        )}

        {/* User Metrics (Commit Metrics, Lines Added/Removed, Contributor Rank) */}
        {(userCommits != null || linesAdded != null || linesRemoved != null || userRank >= 0 || rankScore != null) && (
          <>
            <span className="modal-tiles-heading">{displayName}'s Metrics</span>
            <div className="modal-metric-tiles modal-metric-tiles--2x2">

              {/* Commits (3 columns: total commits by user, % of all project commits, average commits per week */}
              {userCommits != null && (
                <div className="metric-tile metric-tile--multi">
                  <div className="metric-col">
                    <span className="metric-col-value">{userCommits.toLocaleString()}</span>
                    <span className="metric-col-label">Total</span>
                    <span className="metric-col-sub">commits</span>
                  </div>
                  {commitPct != null && (
                    <div className="metric-col">
                      <span className="metric-col-value">{commitPct}%</span>
                      <span className="metric-col-label">Share</span>
                      <span className="metric-col-sub">of project</span>
                    </div>
                  )}
                  {avgCommitsPerWeek != null && (
                    <div className="metric-col">
                      <span className="metric-col-value">{avgCommitsPerWeek}</span>
                      <span className="metric-col-label">Avg</span>
                      <span className="metric-col-sub">per week</span>
                    </div>
                  )}
                </div>
              )}

              {/* Lines (2 columns: lines added, lines removed */}
              {(linesAdded != null || linesRemoved != null) && (
                <div className="metric-tile metric-tile--multi">
                  <div className="metric-col">
                    <span className="metric-col-value metric-col-value--added">+{(linesAdded ?? 0).toLocaleString()}</span>
                    <span className="metric-col-label">Added</span>
                    <span className="metric-col-sub">lines</span>
                  </div>
                  <div className="metric-col">
                    <span className="metric-col-value metric-col-value--removed">-{(linesRemoved ?? 0).toLocaleString()}</span>
                    <span className="metric-col-label">Removed</span>
                    <span className="metric-col-sub">lines</span>
                  </div>
                </div>
              )}

              {/* Contributor rank */}
              {userRank >= 0 && allAuthors.length > 1 && (
                <div className="metric-tile">
                  <div className="metric-col">
                    <span className="metric-col-value">#{userRank + 1}</span>
                    <span className="metric-col-label">Contributor Rank</span>
                    <span className="metric-col-sub">of {allAuthors.length} contributors</span>
                  </div>
                </div>
              )}

              {/* Rank Projects score (essentially how important the user was to each project, ie. for a project with 5 users, each user's score should be roughly 20/100 = 1/5th) */}
              {rankScore != null && (
                <div className="metric-tile">
                  <div className="metric-col">
                    <span className="metric-col-value">{(rankScore * 100).toFixed(0)}<span style={{ fontSize: '0.9em', opacity: 0.5 }}>/100</span></span>
                    <span className="metric-col-label">Rank Score</span>
                    <span className="metric-col-sub">coverage · dominance · team size</span>
                  </div>
                </div>
              )}

            </div>
          </>
        )}

        {/* User Role */}
        {userRole && (
          <div className="modal-section">
            <span className="panel-eyebrow">{displayName}'s Role</span>
            <p className="modal-section-body modal-section-body--primary">
              {userRole.primary_role}{userRole.role_description ? ` - ${userRole.role_description}` : ''}
            </p>
            <p className="modal-section-body">Confidence: {formatRoleConfidence(userRole.confidence)}</p>
            {Array.isArray(userRole.secondary_roles) && userRole.secondary_roles.length > 0 && (
              <p className="modal-section-body" style={{ color: 'var(--text-secondary)' }}>
                Also: {userRole.secondary_roles.join(', ')}
              </p>
            )}
            {breakdownEntries.length > 0 && (
              <div className="chip-cloud modal-chip-cloud-gap">
                {breakdownEntries.map(([cat, pct]) => (
                  <span key={cat} className="detail-chip">
                    {cat}<span className="chip-count">{Math.round(pct)}%</span>
                  </span>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Evidence of Success */}
        {evidence.length > 0 && (
          <div className="modal-section">
            <span className="panel-eyebrow">Evidence of Success</span>
            <div className="modal-evidence-list">
              {evidence.map((ev, i) => (
                <div key={i} className="modal-evidence-item">
                  <p className="modal-section-body modal-section-body--primary">
                    <span className="modal-evidence-type">{ev.type}</span>
                    {ev.description ? ` - ${ev.description}` : ''}
                  </p>
                  {ev.value && <p className="modal-section-body">{ev.value}</p>}
                  {ev.url && (
                    <a className="modal-section-body modal-evidence-link" href={ev.url} target="_blank" rel="noreferrer">
                      {ev.source || ev.url}
                    </a>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Actions */}
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

// --- Skills Timeline Tile ---

const MAX_TIMELINE_SKILLS = 10;

function buildSkillsTimelineData(includedProjects, projectDetails) {
  // Collect data tuples (skill, projectId, projectName, date)
  const entries = [];
  for (const p of includedProjects) {
    const id = p.id ?? p.project_id;
    const detail = projectDetails[id];
    if (!detail) continue;
    const startRaw = detail.git_metrics?.project_start ?? detail.project?.created_at ?? null;
    const dateStr = startRaw ? String(startRaw).slice(0, 10) : null;
    const date = parseIsoDate(dateStr);
    if (!date) continue;
    const skills = Array.isArray(detail.skills) ? detail.skills : [];
    const name = p.display_name ?? p.name ?? '(unnamed)';
    for (const skill of skills) {
      if (skill) entries.push({ skill, projectId: id, projectName: name, date });
    }
  }

  if (entries.length === 0) return { rows: [], minDate: null, maxDate: null };

  // Rank skills by number of distinct projects they appear in
  const skillProjectCounts = new Map();
  for (const e of entries) {
    if (!skillProjectCounts.has(e.skill)) skillProjectCounts.set(e.skill, new Set());
    skillProjectCounts.get(e.skill).add(e.projectId);
  }
  const topSkills = [...skillProjectCounts.entries()]
    .sort((a, b) => b[1].size - a[1].size || a[0].localeCompare(b[0]))
    .slice(0, MAX_TIMELINE_SKILLS)
    .map(([skill]) => skill);

  const topSkillSet = new Set(topSkills);
  const filtered = entries.filter((e) => topSkillSet.has(e.skill));

  const allDates = filtered.map((e) => e.date);
  const minDate = new Date(Math.min(...allDates));
  const maxDate = new Date(Math.max(...allDates));

  // Build rows: one per skill (sorted by earliest appearance)
  const rows = topSkills.map((skill) => {
    const dots = filtered
      .filter((e) => e.skill === skill)
      .sort((a, b) => a.date - b.date)
      .map((e) => ({ projectId: e.projectId, projectName: e.projectName, date: e.date }));
    return { skill, dots };
  });
  rows.sort((a, b) => a.dots[0].date - b.dots[0].date);

  return { rows, minDate, maxDate };
}

function dateToX(date, minDate, maxDate, width) {
  const span = maxDate - minDate || 1;
  return ((date - minDate) / span) * width;
}

// Portal tooltip (renders above all other elements)
function SkillsTooltip({ tooltip }) {
  if (!tooltip) return null;
  const TOOLTIP_W = 220;
  const TOOLTIP_H = 30;
  const GAP = 12;
  // Clamps, so that the tooltip stays within the viewport
  const left = Math.min(tooltip.clientX + GAP, window.innerWidth - TOOLTIP_W - 8);
  const top = tooltip.clientY - TOOLTIP_H - GAP;
  return ReactDOM.createPortal(
    <div
      className="skills-tooltip-portal"
      style={{ left, top, width: TOOLTIP_W }}
      role="tooltip"
    >
      {tooltip.text}
    </div>,
    document.body
  );
}

function SkillsTimeline({ includedProjects, projectDetails }) {
  const [tooltip, setTooltip] = useState(null); // { clientX, clientY, text }
  const containerRef = useRef(null);
  const [containerWidth, setContainerWidth] = useState(0);

  // Measure container width and update on resize
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const ro = new ResizeObserver(([entry]) => {
      setContainerWidth(entry.contentRect.width);
    });
    ro.observe(el);
    setContainerWidth(el.getBoundingClientRect().width);
    return () => ro.disconnect();
  }, []);

  const { rows, minDate } = buildSkillsTimelineData(includedProjects, projectDetails);
  // Right edge is always today
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const maxDate = today;

  if (rows.length === 0) {
    return <p className="tile-placeholder-text">No skill or date data available yet. Scan projects to populate this chart.</p>;
  }

  // Layout constants
  const DOT_R = 5;
  const ROW_H = 28;
  const AXIS_H = 20; 
  const CHART_W = Math.max(containerWidth - 2, 60); 
  const svgH = rows.length * ROW_H + AXIS_H;

  // Date axis ticks (always 5 ticks from minDate to today)
  const span = maxDate - minDate;
  const tickCount = 4;
  const ticks = Array.from({ length: tickCount + 1 }, (_, i) => {
    const d = new Date(minDate.getTime() + (span * i) / tickCount);
    const x = dateToX(d, minDate, maxDate, CHART_W);
    const label = d.toLocaleDateString(undefined, { month: 'short', year: '2-digit' });
    return { x, label };
  });

  const ROW_COLORS = [
    'rgba(74,222,128,0.85)',
    'rgba(52,211,153,0.85)',
    'rgba(34,197,94,0.85)',
    'rgba(16,185,129,0.85)',
    'rgba(5,150,105,0.85)',
    'rgba(74,222,128,0.65)',
    'rgba(52,211,153,0.65)',
    'rgba(34,197,94,0.65)',
    'rgba(16,185,129,0.65)',
    'rgba(5,150,105,0.65)',
  ];

  return (
    <div className="skills-timeline-wrap">
      {/* Two-column layout: HTML "skill label" column & SVG "chart" column */}
      <div className="skills-timeline-body">
        {/* Skill label column */}
        <div className="skills-timeline-labels" style={{ height: rows.length * ROW_H }}>
          {rows.map((row, ri) => (
            <div
              key={row.skill}
              className="skills-timeline-label"
              style={{
                height: ROW_H,
                background: ri % 2 === 0 ? 'rgba(255,255,255,0.015)' : 'transparent',
              }}
            >
              {row.skill}
            </div>
          ))}
        </div>

        {/* SVG chart column */}
        <div className="skills-timeline-chart" ref={containerRef}>
          {containerWidth > 0 && (
            <svg
              width={CHART_W}
              height={svgH}
              style={{ display: 'block', overflow: 'visible' }}
              onMouseLeave={() => setTooltip(null)}
            >
              {/* Vertical grid lines */}
              {ticks.map((t) => (
                <line
                  key={t.label}
                  x1={t.x} y1={0}
                  x2={t.x} y2={rows.length * ROW_H}
                  stroke="rgba(255,255,255,0.07)"
                  strokeWidth="1"
                />
              ))}

              {/* "Today" marker line at right edge */}
              <line
                x1={CHART_W} y1={0}
                x2={CHART_W} y2={rows.length * ROW_H}
                stroke="rgba(74,222,128,0.25)"
                strokeWidth="1"
              />

              {/* Rows */}
              {rows.map((row, ri) => {
                const cy = ri * ROW_H + ROW_H / 2;
                const color = ROW_COLORS[ri % ROW_COLORS.length];
                return (
                  <g key={row.skill}>
                    {/* Row background stripe */}
                    <rect
                      x={0} y={ri * ROW_H}
                      width={CHART_W} height={ROW_H}
                      fill={ri % 2 === 0 ? 'rgba(255,255,255,0.015)' : 'transparent'}
                    />
                    {/* Horizontal track line */}
                    <line
                      x1={0} y1={cy}
                      x2={CHART_W} y2={cy}
                      stroke="rgba(255,255,255,0.1)"
                      strokeWidth="1"
                      strokeDasharray="3 3"
                    />
                    {/* Dots per project */}
                    {row.dots.map((dot) => {
                      const cx = dateToX(dot.date, minDate, maxDate, CHART_W);
                      return (
                        <circle
                          key={`${dot.projectId}-${dot.date.getTime()}`}
                          cx={cx} cy={cy}
                          r={DOT_R}
                          fill={color}
                          stroke="rgba(0,0,0,0.3)"
                          strokeWidth="1"
                          style={{ cursor: 'pointer' }}
                          onMouseEnter={(e) => {
                            setTooltip({
                              clientX: e.clientX,
                              clientY: e.clientY,
                              text: `${dot.projectName} | ${dot.date.toLocaleDateString(undefined, { month: 'short', year: 'numeric' })}`,
                            });
                          }}
                          onMouseMove={(e) => {
                            setTooltip((prev) => prev ? { ...prev, clientX: e.clientX, clientY: e.clientY } : prev);
                          }}
                          onMouseLeave={() => setTooltip(null)}
                        />
                      );
                    })}
                  </g>
                );
              })}

              {/* Date axis labels */}
              {ticks.map((t) => (
                <text
                  key={`tick-${t.label}`}
                  x={t.x} y={rows.length * ROW_H + 14}
                  textAnchor="middle"
                  fontSize="10"
                  fill="rgba(255,255,255,0.35)"
                  fontFamily="inherit"
                >
                  {t.label}
                </text>
              ))}
            </svg>
          )}
        </div>
      </div>

      {/* Summary stats */}
      <div className="heatmap-summary-grid" style={{ marginTop: '0.65rem' }}>
        <div className="heatmap-stat">
          <span className="heatmap-stat-label">Number of Skills Detected</span>
          <span className="heatmap-stat-value">{rows.length}</span>
        </div>
        <div className="heatmap-stat">
          <span className="heatmap-stat-label">Projects with Skills</span>
          <span className="heatmap-stat-value">{includedProjects.length}</span>
        </div>
        <div className="heatmap-stat">
          <span className="heatmap-stat-label">Span of Skill Timeline</span>
          <span className="heatmap-stat-value">
            {minDate && maxDate
              ? `${Math.round((maxDate - minDate) / (1000 * 60 * 60 * 24 * 30))}mo`
              : '-'}
          </span>
        </div>
        <div className="heatmap-stat">
          <span className="heatmap-stat-label">Earliest Skill Detection</span>
          <span className="heatmap-stat-value">
            {minDate ? minDate.toLocaleDateString(undefined, { month: 'short', year: 'numeric' }) : '-'}
          </span>
        </div>
      </div>

      <SkillsTooltip tooltip={tooltip} />
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

function parseIsoDate(value) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value || '')) return null;
  const [year, month, day] = value.split('-').map((item) => Number(item));
  return new Date(year, month - 1, day);
}

function formatIsoDate(date) {
  const year = date.getFullYear();
  const month = `${date.getMonth() + 1}`.padStart(2, '0');
  const day = `${date.getDate()}`.padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function startOfWeekMonday(date) {
  const result = new Date(date);
  const offset = (result.getDay() + 6) % 7;
  result.setDate(result.getDate() - offset);
  result.setHours(0, 0, 0, 0);
  return result;
}

function addDays(date, days) {
  const next = new Date(date);
  next.setDate(next.getDate() + days);
  return next;
}

function buildWeeklyEntries(cells, rangeStart, rangeEnd) {
  const valuesByWeek = new Map(
    (Array.isArray(cells) ? cells : [])
      .filter((cell) => /^\d{4}-\d{2}-\d{2}$/.test(cell?.period || ''))
      .map((item) => [item.period, Number(item.value) || 0])
  );

  const firstCellDate = parseIsoDate(
    [...valuesByWeek.keys()].sort((a, b) => a.localeCompare(b))[0] || ''
  );
  const lastCellDate = parseIsoDate(
    [...valuesByWeek.keys()].sort((a, b) => a.localeCompare(b)).slice(-1)[0] || ''
  );

  const startDate = parseIsoDate(rangeStart) || firstCellDate;
  const endDate = parseIsoDate(rangeEnd) || lastCellDate;
  if (!startDate || !endDate) return [];

  const startWeek = startOfWeekMonday(startDate);
  const endWeek = startOfWeekMonday(endDate);

  const entries = [];
  let cursor = new Date(startWeek);
  while (cursor <= endWeek) {
    const iso = formatIsoDate(cursor);
    entries.push({ period: iso, value: valuesByWeek.get(iso) ?? 0 });
    cursor = addDays(cursor, 7);
  }
  return entries;
}

function formatWeekLabel(isoDate) {
  const parsed = parseIsoDate(isoDate);
  if (!parsed) return isoDate;
  return parsed.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
}

function heatmapCellColor(value, maxValue) {
  if (!value || value <= 0 || maxValue <= 0) return 'rgba(241, 245, 249, 0.08)';
  const ratio = Math.min(1, value / maxValue);
  const alpha = 0.22 + (ratio * 0.78);
  return `rgba(74, 222, 128, ${alpha.toFixed(3)})`;
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
  const [selectedHeatmapProjectId, setSelectedHeatmapProjectId] = useState(null);
  const [heatmapViewScope, setHeatmapViewScope] = useState('project');
  const [projectHeatmaps, setProjectHeatmaps] = useState({});
  const [isLoadingProjectHeatmap, setIsLoadingProjectHeatmap] = useState(false);
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

  // Saved portfolios across all contributors, loaded once contributor list is fully populated
  const [savedPortfolios, setSavedPortfolios] = useState([]);
  const [isLoadingSavedPortfolios, setIsLoadingSavedPortfolios] = useState(false);

  // On portfolio generation we create a "__temp__" DB row (required to support heatmap/timeline endpoints)
  // We use these constants to track whether or not that temp row needs to be deleted (explicity not saved, or app closed before saving)
  const [portfolioIsSaved, setPortfolioIsSaved] = useState(false);

  // Save portfolio modal states
  const [saveModalOpen, setSaveModalOpen] = useState(false);
  const [saveModalName, setSaveModalName] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  // Rename state for saved portfolio list
  const [renamingPortfolioId, setRenamingPortfolioId] = useState(null);
  const [renameValue, setRenameValue] = useState('');

  // Delete any "__temp__" rows left behind by a previous abrupt/unintentional close
  useEffect(() => {
    axios.delete(`${API_BASE_URL}/portfolios/cleanup-temp`).catch(() => {});
  }, []);

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

  // Fetch all saved portfolios in a single request (excludes __temp__ rows)
  useEffect(() => {
    setIsLoadingSavedPortfolios(true);
    axios
      .get(`${API_BASE_URL}/portfolios/all`)
      .then((res) => setSavedPortfolios(Array.isArray(res.data) ? res.data : []))
      .catch(() => setSavedPortfolios([]))
      .finally(() => setIsLoadingSavedPortfolios(false));
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

  const loadProjectHeatmap = async (portfolioIdValue, project, viewScope = 'project') => {
    const projectId = project?.id ?? project?.project_id;
    if (!portfolioIdValue || !projectId) return;

    const cacheKey = `${projectId}:${viewScope}`;
    if (projectHeatmaps[cacheKey]) return;

    setIsLoadingProjectHeatmap(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/web/portfolio/${portfolioIdValue}/heatmap/project`, {
        params: {
          project_id: projectId,
          granularity: 'week',
          metric: 'contrib_files',
          mode: 'private',
          view_scope: viewScope,
        },
      });
      setProjectHeatmaps((prev) => ({ ...prev, [cacheKey]: response.data }));
    } catch (err) {
      showToast(err?.response?.data?.detail || err.message || 'Failed to load project heatmap.', 'error');
    } finally {
      setIsLoadingProjectHeatmap(false);
    }
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
      // Create a temporary DB row to drive the heatmap/timeline (visualization) endpoints.
      // Named with the "__temp__" flag so it can be deleted if the app closes mid-session.
      const saveRes = await axios.post(`${API_BASE_URL}/portfolios`, {
        username,
        portfolio_name: `__temp__${username}`,
        display_name: null,
        included_project_ids: eligible.map((p) => p.id ?? p.project_id),
        featured_project_ids: [],
      });
      const portfolio_id = saveRes.data.id;
      setPortfolioId(portfolio_id);
      setPortfolioIsSaved(false); // Temp row, not yet explicitly saved by user

      // Retrieve all relevant data for the web portfolio (fetched in parallel)
      const [metaRes, showcaseRes, heatmapRes, timelineRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/portfolios/${portfolio_id}`),
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

      const initialProject = eligible[0] ?? null;
      const initialProjectId = initialProject ? (initialProject.id ?? initialProject.project_id) : null;
      setSelectedHeatmapProjectId(initialProjectId);
      setHeatmapViewScope('project');
      setProjectHeatmaps({});
      if (initialProject) {
        await loadProjectHeatmap(portfolio_id, initialProject, 'project');
      }

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
    // If the user never explicitly saved the portfolio, delete the temp DB row that was created on generation
    if (portfolioId !== null && !portfolioIsSaved) {
      axios.delete(`${API_BASE_URL}/portfolios/${portfolioId}`).catch(() => {});
    }
    setPortfolioIsSaved(false);
    setPhase('setup');
    setPortfolioId(null);
    setPortfolioMeta(null);
    setHeatmapData({ cells: [], max_value: 0 });
    setTimelineData([]);
    setSelectedHeatmapProjectId(null);
    setHeatmapViewScope('project');
    setProjectHeatmaps({});
    setIsLoadingProjectHeatmap(false);
    setProjectSearch('');
    setIncludedProjects([]);
    setFeaturedIds(new Set());
    setProjectDetails({});
    setExpandedProjectId(null);
    clearTimeout(toastTimer.current);
    setToast(null);
  };

  // Save the current dashboard state, updates the existing temp row in-place (no new DB row)
  const handleSavePortfolio = async () => {
    const name = saveModalName.trim();
    if (!name) {
      showToast('Please enter a name for your portfolio.', 'error');
      return;
    }
    setIsSaving(true);
    try {
      const featuredProjectIds = includedProjects
        .filter((p) => featuredIds.has(p.display_name ?? p.name))
        .map((p) => p.id ?? p.project_id);
      const res = await axios.put(`${API_BASE_URL}/portfolios/${portfolioId}`, {
        portfolio_name: name,
        display_name: legalName.trim() || null,
        included_project_ids: includedProjects.map((p) => p.id ?? p.project_id),
        featured_project_ids: featuredProjectIds,
      });
      // Update the saved list, replace if already present, otherwise add
      setSavedPortfolios((prev) => {
        const exists = prev.some((p) => p.id === portfolioId);
        return exists
          ? prev.map((p) => (p.id === portfolioId ? res.data : p))
          : [res.data, ...prev];
      });
      setPortfolioIsSaved(true);
      setSaveModalOpen(false);
      setSaveModalName('');
      showToast(`Portfolio "${name}" saved.`, 'success');
    } catch (err) {
      showToast(err?.response?.data?.detail || err.message || 'Failed to save portfolio.', 'error');
    } finally {
      setIsSaving(false);
    }
  };

  // Restore/rebuild a saved portfolio (re-fetch all visualisation data and enter dashboard phase)
  const handleLoadPortfolio = async (saved) => {
    setIsGenerating(true);
    try {
      const eligible = allProjects.filter((p) =>
        (saved.included_project_ids || []).includes(p.id ?? p.project_id)
      );
      setUsername(saved.username);
      setLegalName(saved.display_name || '');
      setExcludedProjectIds([]);
      setIncludedProjects(eligible);

      const portfolio_id = saved.id;
      setPortfolioId(portfolio_id);

      const [metaRes, showcaseRes, heatmapRes, timelineRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/portfolios/${portfolio_id}`),
        axios.get(`${API_BASE_URL}/web/portfolio/${portfolio_id}/showcase?limit=3`),
        axios.get(`${API_BASE_URL}/web/portfolio/${portfolio_id}/heatmap?granularity=day`),
        axios.get(`${API_BASE_URL}/web/portfolio/${portfolio_id}/timeline?granularity=month`),
      ]);

      setPortfolioMeta(metaRes.data);
      setHeatmapData(heatmapRes.data);
      setTimelineData(timelineRes.data.timeline || []);

      const detailResults = await Promise.allSettled(
        eligible.map((p) => axios.get(`${API_BASE_URL}/projects/${p.id ?? p.project_id}`))
      );
      const detailMap = {};
      detailResults.forEach((result, i) => {
        const id = eligible[i].id ?? eligible[i].project_id;
        if (result.status === 'fulfilled') detailMap[id] = result.value.data ?? null;
      });
      setProjectDetails(detailMap);

      const featuredNames = new Set(
        eligible
          .filter((p) => (saved.featured_project_ids || []).includes(p.id ?? p.project_id))
          .map((p) => p.display_name ?? p.name)
      );
      if (featuredNames.size === 0) {
        const top = (showcaseRes.data.projects || []).slice(0, MAX_FEATURED).map((p) => p.name ?? p.display_name);
        top.forEach((n) => featuredNames.add(n));
      }
      setFeaturedIds(featuredNames);

      const initialProject = eligible[0] ?? null;
      const initialProjectId = initialProject ? (initialProject.id ?? initialProject.project_id) : null;
      setSelectedHeatmapProjectId(initialProjectId);
      setHeatmapViewScope('project');
      setProjectHeatmaps({});
      if (initialProject) await loadProjectHeatmap(portfolio_id, initialProject, 'project');

      setPortfolioIsSaved(true); // loaded from an existing saved record - do not delete on back
      setPhase('dashboard');
    } catch (err) {
      showToast(err?.response?.data?.detail || err.message || 'Failed to load portfolio.', 'error');
    } finally {
      setIsGenerating(false);
    }
  };

  // Delete a saved portfolio entry from the DB
  const handleDeletePortfolio = async (portfolioIdToDelete, portfolioName) => {
    if (!window.confirm(`Delete "${portfolioName}"? This cannot be undone.`)) return;
    try {
      await axios.delete(`${API_BASE_URL}/portfolios/${portfolioIdToDelete}`);
      setSavedPortfolios((prev) => prev.filter((p) => p.id !== portfolioIdToDelete));
      showToast('Portfolio deleted.', 'success');
    } catch (err) {
      showToast(err?.response?.data?.detail || err.message || 'Failed to delete portfolio.', 'error');
    }
  };

  // Rename a saved portfolio
  const handleRenamePortfolio = async (portfolioIdToRename) => {
    const name = renameValue.trim();
    if (!name) { setRenamingPortfolioId(null); return; }
    try {
      const res = await axios.patch(`${API_BASE_URL}/portfolios/${portfolioIdToRename}/name`, {
        portfolio_name: name,
      });
      setSavedPortfolios((prev) =>
        prev.map((p) => (p.id === portfolioIdToRename ? { ...p, portfolio_name: res.data.portfolio_name } : p))
      );
      setRenamingPortfolioId(null);
    } catch (err) {
      showToast(err?.response?.data?.detail || err.message || 'Failed to rename portfolio.', 'error');
    }
  };

  // Store display name for web portfolio header
  const displayName = legalName.trim() || username;

  const selectedHeatmapProject = includedProjects.find(
    (project) => (project.id ?? project.project_id) === selectedHeatmapProjectId
  ) ?? null;
  const selectedHeatmapKey = selectedHeatmapProject
    ? `${selectedHeatmapProject.id ?? selectedHeatmapProject.project_id}:${heatmapViewScope}`
    : null;
  const selectedHeatmap = selectedHeatmapProject
    ? projectHeatmaps[selectedHeatmapKey]
    : null;
  const heatmapEntries = buildWeeklyEntries(
    selectedHeatmap?.cells || [],
    selectedHeatmap?.range_start,
    selectedHeatmap?.range_end
  );
  const heatmapMax = Math.max(selectedHeatmap?.max_value || 0, 1);
  const heatmapUnit = selectedHeatmap?.value_unit === 'commits' ? 'commit(s)' : 'contributed file(s)';
  const heatmapStartLabel = selectedHeatmap?.range_start
    ? formatWeekLabel(selectedHeatmap.range_start)
    : null;
  const heatmapEndLabel = selectedHeatmap?.range_end
    ? formatWeekLabel(selectedHeatmap.range_end)
    : null;
  const totalHeatmapValue = heatmapEntries.reduce((sum, item) => sum + (item.value || 0), 0);
  const activeWeeks = heatmapEntries.filter((item) => (item.value || 0) > 0).length;
  const avgActiveWeek = activeWeeks > 0 ? Math.round((totalHeatmapValue / activeWeeks) * 10) / 10 : 0;
  const consistencyPct = heatmapEntries.length > 0
    ? Math.round((activeWeeks / heatmapEntries.length) * 100)
    : 0;
  const recentWeeksTotal = heatmapEntries.slice(-4).reduce((sum, item) => sum + (item.value || 0), 0);
  const prevWeeksTotal = heatmapEntries.slice(-8, -4).reduce((sum, item) => sum + (item.value || 0), 0);
  const trendText = recentWeeksTotal > prevWeeksTotal
    ? 'Increasing'
    : recentWeeksTotal < prevWeeksTotal
      ? 'Cooling'
      : 'Stable';

  // Summary line in portfolio header (e.g. "XX projects | Generated on X/X/XXXX") [TODO: update later to be a user-centric summary]
  const headerSummary = portfolioMeta
    ? `${(portfolioMeta.included_project_ids ?? []).length} projects | Generated on ${new Date(portfolioMeta.created_at).toLocaleDateString()}`
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
          <button
            type="button"
            onClick={() => {
              setSaveModalName('');
              setSaveModalOpen(true);
            }}
          >
            Save Portfolio
          </button>
        </div>

        {/* Save Portfolio modal */}
        {saveModalOpen && (
          <div className="modal-overlay" role="dialog" aria-modal="true" aria-label="Save Portfolio">
            <div className="modal-box" style={{ maxWidth: 420 }}>
              <h3 style={{ marginTop: 0 }}>Save Portfolio</h3>
              <label className="portfolio-form-label">
                Portfolio Name
                <input
                  type="text"
                  className="portfolio-input"
                  value={saveModalName}
                  onChange={(e) => setSaveModalName(e.target.value)}
                  onKeyDown={(e) => { if (e.key === 'Enter') handleSavePortfolio(); }}
                  autoFocus
                />
              </label>
              <div className="portfolio-form-actions" style={{ marginTop: '1rem' }}>
                <button type="button" onClick={handleSavePortfolio} disabled={isSaving}>
                  {isSaving ? 'Saving…' : 'Save'}
                </button>
                <button
                  type="button"
                  className="secondary"
                  onClick={() => { setSaveModalOpen(false); setSaveModalName(''); }}
                  disabled={isSaving}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

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

          {/* Visualization Tiles: Activity Heatmap & Skills Timeline*/}
            <section className="portfolio-tile">
              <h3 className="tile-heading">Activity Heatmap</h3>
              <div className="heatmap-toolbar">
                <div className="heatmap-view-toggle" role="group" aria-label="Heatmap view mode">
                  <button
                    type="button"
                    className={`heatmap-view-btn${heatmapViewScope === 'project' ? ' active' : ''}`}
                    onClick={async () => {
                      setHeatmapViewScope('project');
                      if (selectedHeatmapProject) {
                        await loadProjectHeatmap(portfolioId, selectedHeatmapProject, 'project');
                      }
                    }}
                  >
                    Project View
                  </button>
                  <button
                    type="button"
                    className={`heatmap-view-btn${heatmapViewScope === 'user' ? ' active' : ''}`}
                    onClick={async () => {
                      setHeatmapViewScope('user');
                      if (selectedHeatmapProject) {
                        await loadProjectHeatmap(portfolioId, selectedHeatmapProject, 'user');
                      }
                    }}
                  >
                    Per User View
                  </button>
                </div>
                <label className="portfolio-form-label" style={{ margin: 0 }}>
                  Project
                  <select
                    className="portfolio-select heatmap-project-select"
                    value={selectedHeatmapProjectId ?? ''}
                    onChange={async (e) => {
                      const nextProjectId = Number(e.target.value);
                      setSelectedHeatmapProjectId(nextProjectId);
                      const project = includedProjects.find((p) => (p.id ?? p.project_id) === nextProjectId);
                      if (project) {
                        await loadProjectHeatmap(portfolioId, project, heatmapViewScope);
                      }
                    }}
                  >
                    {includedProjects.map((project) => {
                      const id = project.id ?? project.project_id;
                      return (
                        <option key={id} value={id}>
                          {project.display_name ?? project.name}
                        </option>
                      );
                    })}
                  </select>
                </label>
              </div>

              <div className="heatmap-panel">
                {isLoadingProjectHeatmap && <p className="tile-placeholder-text">Loading contribution activity...</p>}

                {!isLoadingProjectHeatmap && selectedHeatmap && heatmapEntries.length > 0 && (
                  <>
                    <div className="heatmap-summary-grid">
                      <div className="heatmap-stat">
                        <span className="heatmap-stat-label">Total</span>
                        <span className="heatmap-stat-value">{totalHeatmapValue} {heatmapUnit}</span>
                      </div>
                      <div className="heatmap-stat">
                        <span className="heatmap-stat-label">Active Weeks</span>
                        <span className="heatmap-stat-value">{activeWeeks}/{heatmapEntries.length}</span>
                      </div>
                      <div className="heatmap-stat">
                        <span className="heatmap-stat-label">Consistency</span>
                        <span className="heatmap-stat-value">{consistencyPct}%</span>
                      </div>
                      <div className="heatmap-stat">
                        <span className="heatmap-stat-label">Trend (4w)</span>
                        <span className="heatmap-stat-value">{trendText}</span>
                      </div>
                    </div>

                    <div className="heatmap-scroll-wrap" aria-label="Project contribution heatmap">
                      <div className="heatmap-scroll-content">
                        <div className="project-heatmap-grid">
                          {heatmapEntries.map((cell) => (
                            <span
                              key={cell.period}
                              className="heatmap-cell heatmap-cell--week"
                              title={`Week of ${cell.period}: ${cell.value} ${heatmapUnit}`}
                              style={{ backgroundColor: heatmapCellColor(cell.value, heatmapMax) }}
                            />
                          ))}
                        </div>
                        <div className="project-heatmap-weeks" aria-hidden="true">
                          {heatmapEntries.map((cell, index) => (
                            <span key={`label-${cell.period}`} className="heatmap-week-label">
                              {index % 6 === 0 || index === heatmapEntries.length - 1 ? formatWeekLabel(cell.period) : ''}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                    <div className="heatmap-legend" aria-hidden="true">
                      <span className="heatmap-legend-text">Less</span>
                      <span className="heatmap-legend-swatch" style={{ backgroundColor: heatmapCellColor(1, heatmapMax) }} />
                      <span className="heatmap-legend-swatch" style={{ backgroundColor: heatmapCellColor(Math.ceil(heatmapMax * 0.5), heatmapMax) }} />
                      <span className="heatmap-legend-swatch" style={{ backgroundColor: heatmapCellColor(heatmapMax, heatmapMax) }} />
                      <span className="heatmap-legend-text">More</span>
                    </div>
                    <div className="heatmap-meta">
                      <span>
                        {selectedHeatmapProject?.display_name ?? selectedHeatmapProject?.name} 
                      </span>
                      <span>
                        Duration: {heatmapStartLabel || 'N/A'} - {heatmapEndLabel || 'N/A'}
                      </span>
                      <span>
                        Peak week: {selectedHeatmap.max_value || 0} {heatmapUnit}
                      </span>
                      <span>
                        Avg active week: {avgActiveWeek} {heatmapUnit}
                      </span>
                    </div>
                  </>
                )}

                {!isLoadingProjectHeatmap && selectedHeatmap && heatmapEntries.length === 0 && (
                  <p className="tile-placeholder-text">
                    {heatmapViewScope === 'user'
                      ? `No activity found for ${username} in this project yet.`
                      : 'No project activity found for this project yet.'}
                  </p>
                )}

                {!isLoadingProjectHeatmap && !selectedHeatmap && (
                  <p className="tile-placeholder-text">Select a project to view contribution activity.</p>
                )}
              </div>
            </section>
            <section className="portfolio-tile">
              <h3 className="tile-heading">Skills Timeline</h3>
              <SkillsTimeline includedProjects={includedProjects} projectDetails={projectDetails} />
            </section>

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
                <option value="">- select a contributor -</option>
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

      {/* Saved Portfolios tile */}
      <section className="portfolio-setup-panel" style={{ marginTop: '1.5rem' }}>
        <h2>Saved Portfolios</h2>
        {isLoadingSavedPortfolios && <p className="portfolio-hint">Loading saved portfolios…</p>}
        {!isLoadingSavedPortfolios && savedPortfolios.length === 0 && (
          <p className="portfolio-hint">No saved portfolios yet. Generate a portfolio and click <strong>Save Portfolio</strong>.</p>
        )}
        {!isLoadingSavedPortfolios && savedPortfolios.length > 0 && (
          <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
            {savedPortfolios.map((p) => (
              <li
                key={p.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.6rem',
                  padding: '0.55rem 0.8rem',
                  background: 'var(--surface, #1e2a1e)',
                  borderRadius: '0.5rem',
                  flexWrap: 'wrap',
                }}
              >
                {/* Name/rename inline editor */}
                {renamingPortfolioId === p.id ? (
                  <input
                    type="text"
                    className="portfolio-input"
                    style={{ flex: 1, minWidth: 120 }}
                    value={renameValue}
                    onChange={(e) => setRenameValue(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') handleRenamePortfolio(p.id);
                      if (e.key === 'Escape') setRenamingPortfolioId(null);
                    }}
                    autoFocus
                  />
                ) : (
                  <span style={{ flex: 1, fontWeight: 600, fontSize: '0.95rem' }}>
                    {p.portfolio_name}
                    <span style={{ fontWeight: 400, fontSize: '0.8rem', color: '#7a9a7a', marginLeft: '0.5rem' }}>
                      {p.username} · {new Date(p.created_at).toLocaleDateString()}
                    </span>
                  </span>
                )}

                {/* Action buttons */}
                {renamingPortfolioId === p.id ? (
                  <>
                    <button type="button" onClick={() => handleRenamePortfolio(p.id)}>Save</button>
                    <button type="button" className="secondary" onClick={() => setRenamingPortfolioId(null)}>Cancel</button>
                  </>
                ) : (
                  <>
                    <button type="button" disabled={isGenerating} onClick={() => handleLoadPortfolio(p)}>
                      {isGenerating ? 'Loading…' : 'View'}
                    </button>
                    <button type="button" className="secondary" onClick={() => { setRenamingPortfolioId(p.id); setRenameValue(p.portfolio_name); }}>
                      Rename
                    </button>
                    <button type="button" className="danger" onClick={() => handleDeletePortfolio(p.id, p.portfolio_name)}>
                      Delete
                    </button>
                  </>
                )}
              </li>
            ))}
          </ul>
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
