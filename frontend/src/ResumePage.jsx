import React, { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import { showModal } from "./modal.js";

function ResumePage({ onBack }) {
  const [contributors, setContributors] = useState([]);
  const [username, setUsername] = useState("");
  const [resumeContent, setResumeContent] = useState("");
  const [editContent, setEditContent] = useState("");
  const [resumeId, setResumeId] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [copied, setCopied] = useState(false);
  const [llmConsentGranted, setLlmConsentGranted] = useState(false);
  const [isConfigLoaded, setIsConfigLoaded] = useState(false);
  const [llmSummary, setLlmSummary] = useState(false);
  const [, setShowConsentPanel] = useState(false);
  const [resumeHistory, setResumeHistory] = useState([]);
  const [deletingId, setDeletingId] = useState(null);
  const [allProjects, setAllProjects] = useState([]);
  const [userProjects, setUserProjects] = useState([]);
  const [includedProjectIds, setIncludedProjectIds] = useState([]);
  const [isLoadingUserProjects, setIsLoadingUserProjects] = useState(false);
  const [isProjectsTransitioning, setIsProjectsTransitioning] = useState(false);
  const [education, setEducation] = useState([
    {
      school: "",
      degree: "",
      field: "",
      start: "",
      end: "",
      gpa: "",
    },
  ]);
  const [openIndex, setOpenIndex] = useState(null);

  const createEmptyEducation = () => ({
    school: "",
    degree: "",
    field: "",
    start: "",
    end: "",
    gpa: "",
  });

  const selectedUsername = username.trim();
  const hasScannedProjects = allProjects.length > 0;
  const isContributorSelected = selectedUsername.length > 0;
  const isValidContributor = contributors.includes(selectedUsername);
  const hasSelectedProjects = includedProjectIds.length > 0;
  const canGenerate = isValidContributor && hasScannedProjects && hasSelectedProjects && !isLoading;

  useEffect(() => {
    fetch("http://127.0.0.1:8000/contributors")
      .then((r) => r.ok ? r.json() : Promise.reject())
      .then(setContributors)
      .catch(() => console.error("Contributor fetch failed"));

    fetch("http://127.0.0.1:8000/config")
      .then((r) => r.ok ? r.json() : Promise.reject())
      .then((cfg) => {
        setLlmConsentGranted(Boolean(cfg.llm_resume_consent));
      })
      .catch(() => {
        setLlmConsentGranted(false);
      })
      .finally(() => {
        setIsConfigLoaded(true);
      });

    fetch("http://127.0.0.1:8000/projects")
      .then((r) => r.ok ? r.json() : Promise.reject())
      .then((projects) => {
        setAllProjects(Array.isArray(projects) ? projects : []);
      })
      .catch(() => {
        setAllProjects([]);
      });
  }, []);

  const fetchHistory = (user) => {
    const u = (user || "").trim();
    const url = u
      ? `http://127.0.0.1:8000/resumes?username=${encodeURIComponent(u)}`
      : "http://127.0.0.1:8000/resumes";
    fetch(url)
      .then((r) => r.ok ? r.json() : [])
      .then(setResumeHistory)
      .catch(() => setResumeHistory([]));
  };

  useEffect(() => {
    fetchHistory(username);
  }, [username]);

  useEffect(() => {
    let transitionTimer;
    let isCancelled = false;

    if (!username.trim()) {
      setUserProjects([]);
      setIncludedProjectIds([]);
      setIsLoadingUserProjects(false);
      setIsProjectsTransitioning(false);
      return;
    }

    setIsLoadingUserProjects(true);
    setIsProjectsTransitioning(true);
    setUserProjects([]);
    setIncludedProjectIds([]);

    fetch(`http://127.0.0.1:8000/rank-projects?mode=contributor&contributor_name=${encodeURIComponent(username.trim())}`)
      .then((r) => r.ok ? r.json() : Promise.reject())
      .then((ranked) => {
        const rankedNames = new Set((Array.isArray(ranked) ? ranked : []).map((item) => item.project));
        const projects = allProjects.filter((project) => rankedNames.has(project.name));
        const projectIds = projects
          .map((project) => project.id ?? project.project_id)
          .filter((projectId) => projectId != null);
        transitionTimer = setTimeout(() => {
          if (isCancelled) return;
          setUserProjects(projects);
          setIncludedProjectIds(projectIds);
          setIsLoadingUserProjects(false);
          setIsProjectsTransitioning(false);
        }, 130);
      })
      .catch(() => {
        if (isCancelled) return;
        transitionTimer = setTimeout(() => {
          if (isCancelled) return;
          setUserProjects([]);
          setIncludedProjectIds([]);
          setIsLoadingUserProjects(false);
          setIsProjectsTransitioning(false);
        }, 130);
      });

    return () => {
      isCancelled = true;
      if (transitionTimer) clearTimeout(transitionTimer);
    };
  }, [username, allProjects]);

  const toggleInclude = (id) => {
    setIncludedProjectIds((prev) => (
      prev.includes(id)
        ? prev.filter((projectId) => projectId !== id)
        : [...prev, id]
    ));
  };

  const handleEducationChange = (index, field, value) => {
    setEducation((prev) => prev.map((item, i) => (
      i === index ? { ...item, [field]: value } : item
    )));
  };

  const addEducation = () => {
    const last = education[education.length - 1];

    const isEmpty =
      !last.school &&
      !last.degree &&
      !last.field;

    if (isEmpty) return;

    setEducation((prev) => {
      const next = [...prev, createEmptyEducation()];
      setOpenIndex(next.length - 1);
      return next;
    });
  };

  const removeEducation = (index) => {
    setEducation((prev) => {
      const next = prev.filter((_, i) => i !== index);
      setOpenIndex((current) => {
        if (!next.length) return null;
        if (current == null) return 0;
        if (current === index) return Math.min(index, next.length - 1);
        if (current > index) return current - 1;
        return Math.min(current, next.length - 1);
      });
      return next;
    });
  };
  const handleSelectAllProjects = () => {
    setIncludedProjectIds(
      userProjects
        .map((project) => project.id ?? project.project_id)
        .filter((projectId) => projectId != null)
    );
  };

  const handleDeselectAllProjects = () => {
    setIncludedProjectIds([]);
  };

  const loadResumeById = async (id) => {
    setError("");
    try {
      const res = await fetch(`http://127.0.0.1:8000/resume/${id}`);
      if (!res.ok) throw new Error("Failed to retrieve selected resume.");
      const payload = await res.json();
      setResumeId(payload.id);
      setResumeContent(payload.content || "");
      setEditContent(payload.content || "");
      setIsEditing(false);
    } catch (err) {
      setError(err.message || "Unexpected error occurred.");
    }
  };

  const handleGenerateResume = async () => {
    setError(""); setResumeContent(""); setResumeId(null); setIsLoading(true);

    if (!isValidContributor) {
      setError("Please select a contributor.");
      setIsLoading(false);
      return;
    }

    if (!hasScannedProjects) {
      setError("Please scan a project to generate a resume.");
      setIsLoading(false);
      return;
    }

    if (!hasSelectedProjects) {
      setError("Select at least one project to include.");
      setIsLoading(false);
      return;
    }

    const excludedProjectNames = userProjects
      .filter((project) => {
        const projectId = project.id ?? project.project_id;
        return projectId != null && !includedProjectIds.includes(projectId);
      })
      .map((project) => project.name)
      .filter(Boolean);
    const cleanedEducation = education.filter((edu) =>
      edu.school.trim() ||
      edu.degree.trim() ||
      edu.field.trim()
    );

    try {
      const gen = await fetch("http://127.0.0.1:8000/resume/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: selectedUsername,
          save_to_db: true,
          llm_summary: llmSummary,
          excluded_project_names: excludedProjectNames,
          education: cleanedEducation,
        }),
      });
      if (!gen.ok) {
        const { detail } = await gen.json().catch(() => ({}));
        throw new Error(detail || `Error ${gen.status}: Resume generation failed.`);
      }
      const { resume_id } = await gen.json();
      setResumeId(resume_id);

      const res = await fetch(`http://127.0.0.1:8000/resume/${resume_id}`);
      if (!res.ok) throw new Error("Failed to retrieve generated resume.");
      const { content } = await res.json();
      setResumeContent(content);
      setEditContent(content);
      setIsEditing(false);
      fetchHistory(selectedUsername);
    } catch (err) {
      setError(err.message || "Unexpected error occurred.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveEdit = async () => {
    setIsSaving(true);
    try {
      const res = await fetch(`http://127.0.0.1:8000/resume/${resumeId}/edit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: editContent }),
      });
      if (!res.ok) throw new Error("Failed to save edits.");
      setResumeContent(editContent);
      setIsEditing(false);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsSaving(false);
    }
  };

  const handleDeleteResume = async (id, e) => {
    e.stopPropagation();

    const confirmed = await showModal({
      type: "danger",
      title: "Delete Resume",
      message: "Delete this resume? This cannot be undone.",
      confirmText: "Delete",
      cancelText: "Cancel",
    });

    if (!confirmed) return;

    setDeletingId(id);
    try {
      const res = await fetch(`http://127.0.0.1:8000/resume/${id}`, { method: "DELETE" });
      if (!res.ok) throw new Error("Failed to delete resume.");
      if (resumeId === id) {
        setResumeContent("");
        setResumeId(null);
        setEditContent("");
        setIsEditing(false);
      }
      fetchHistory(username);
    } catch (err) {
      setError(err.message);
    } finally {
      setDeletingId(null);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(resumeContent).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  const downloadResume = () => {
    const blob = new Blob([resumeContent], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    Object.assign(document.createElement("a"), { href: url, download: `resume_${selectedUsername || "resume"}.md` }).click();
    URL.revokeObjectURL(url);
  };

  const downloadTxt = () => {
    const plainText = resumeContent
      .replace(/^#{1,6}\s*/gm, "")
      .replace(/\*\*/g, "")
      .replace(/^\s*[-*]\s+/gm, "");
    const blob = new Blob([plainText], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    Object.assign(document.createElement("a"), { href: url, download: `resume_${selectedUsername || "resume"}.txt` }).click();
    URL.revokeObjectURL(url);
  };

  const downloadPdf = async () => {
    setError("");
    if (!resumeId) {
      setError("Select or generate a saved resume before downloading PDF.");
      return;
    }

    try {
      const infoResponse = await fetch(`http://127.0.0.1:8000/resume/${resumeId}/pdf/info`);
      if (!infoResponse.ok) {
        const { detail } = await infoResponse.json().catch(() => ({}));
        throw new Error(detail || "Failed to inspect PDF export.");
      }

      const pdfInfo = await infoResponse.json();
      if (pdfInfo.page_count > 1) {
        const confirmed = await showModal({
          type: "warning",
          title: "Resume Exceeds One Page",
          message: `This exported PDF is ${pdfInfo.page_count} pages long. Continue exporting, or go back and edit your resume first.`,
          confirmText: "Continue Exporting",
          cancelText: "Go Back and Edit",
        });

        if (!confirmed) {
          return;
        }
      }

      const response = await fetch(`http://127.0.0.1:8000/resume/${resumeId}/pdf`);
      if (!response.ok) {
        const { detail } = await response.json().catch(() => ({}));
        throw new Error(detail || "Failed to generate PDF.");
      }

      const blob = await response.blob();
      const contentDisposition = response.headers.get("Content-Disposition") || "";
      const filenameMatch = contentDisposition.match(/filename="?([^";]+)"?/i);
      const filename = filenameMatch?.[1] || `resume_${selectedUsername || "resume"}.pdf`;

      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = filename;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err.message || "Unexpected error occurred.");
    }
  };

  const formatGeneratedAt = (value) => {
    if (!value) return "Unknown date";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return value;
    return date.toLocaleString();
  };

  return (
    <div className="page-shell">
      <style>{`
  .resume-markdown h1 { font-size: 1.4rem; font-weight: 700; margin: 0 0 0.25rem; color: var(--text-primary); }
  .resume-markdown h2 { font-size: 0.72rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: var(--text-muted); margin: 1.5rem 0 0.6rem; border-bottom: 1px solid var(--border); padding-bottom: 0.4rem; }
  .resume-markdown h3 { font-size: 0.95rem; font-weight: 600; color: var(--accent-cyan); margin: 1rem 0 0.3rem; }
  .resume-markdown p { color: var(--text-secondary); font-size: 0.88rem; margin: 0.3rem 0; }
  .resume-markdown ul { padding-left: 1.2rem; margin: 0.4rem 0; list-style-type: disc; }
  .resume-markdown li { color: var(--text-secondary); font-size: 0.88rem; margin-bottom: 0.25rem; display: list-item; }
  .resume-markdown strong { color: var(--text-primary); font-weight: 600; }
  .resume-markdown em { color: var(--text-muted); font-style: italic; }
  .resume-markdown hr { border: none; border-top: 1px solid var(--border); margin: 1rem 0; }
  .resume-markdown code { font-family: 'DM Mono', monospace; font-size: 0.82rem; background: rgba(255,255,255,0.06); padding: 0.1rem 0.35rem; border-radius: 4px; color: var(--accent-green); }
  .project-list-shell { transition: opacity 220ms ease, transform 220ms ease; }
  .project-list-shell.is-loading { opacity: 0.62; transform: translateY(6px); }
  .project-list-shell.is-ready { opacity: 1; transform: translateY(0); }
  .project-skeleton-row {
    height: 28px;
    border-radius: var(--radius-sm);
    border: 1px solid var(--border);
    background: linear-gradient(90deg, rgba(255,255,255,0.03), rgba(255,255,255,0.08), rgba(255,255,255,0.03));
    background-size: 200% 100%;
    animation: projectSkeletonPulse 1.2s ease-in-out infinite;
  }
  @keyframes projectSkeletonPulse {
    0% { background-position: 200% 0; opacity: 0.55; }
    50% { opacity: 0.9; }
    100% { background-position: -200% 0; opacity: 0.55; }
  }
`}</style>
      <header className="app-header">
        <h1>Generate Resume</h1>
        <p>Create a contributor-focused resume from project data.</p>
      </header>

      <div className="scan-layout grid gap-5" style={{ gridTemplateColumns: "280px 1fr", alignItems: "start" }}>
        <aside className="projects-list-panel" style={{ paddingLeft: "1.75rem" }}>
          <h2>Previous Resumes</h2>
          <div className="grid gap-2 overflow-y-auto" style={{ maxHeight: "calc(100vh - 280px)", overflowY: "auto", paddingRight: "0.4rem" }}>
            {resumeHistory.length === 0 && (
              <p style={{ margin: 0, color: "var(--text-muted)", fontSize: "0.82rem" }}>
                No saved resumes for this contributor yet.
              </p>
            )}
            {resumeHistory.map((item) => {
              const isSelected = item.id === resumeId;
              return (
                <div
                  key={item.id}
                  className="recent-item"
                  role="button"
                  tabIndex={0}
                  onClick={() => loadResumeById(item.id)}
                  onKeyDown={(event) => {
                    if (event.key === "Enter" || event.key === " ") {
                      event.preventDefault();
                      loadResumeById(item.id);
                    }
                  }}
                  style={{
                    position: "relative",
                    cursor: "pointer",
                    borderColor: isSelected ? "rgba(74, 222, 128, 0.45)" : undefined,
                    background: isSelected ? "rgba(74, 222, 128, 0.06)" : undefined,
                    boxShadow: isSelected ? "0 0 0 1px rgba(74, 222, 128, 0.2)" : undefined,
                  }}
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="recent-title" style={{ margin: 0 }}>{item.username || "Unknown contributor"}</span>
                    <span
                      style={{
                        fontFamily: "DM Mono, monospace",
                        background: "var(--bg-surface-md)",
                        border: "1px solid var(--border)",
                        borderRadius: "5px",
                        padding: "1px 6px",
                        fontSize: "0.72rem",
                        color: "var(--text-secondary)",
                      }}
                    >
                      #{item.id}
                    </span>
                  </div>
                  <div className="recent-meta">{formatGeneratedAt(item.generated_at)}</div>
                  <button
                    onClick={(e) => handleDeleteResume(item.id, e)}
                    disabled={deletingId === item.id}
                    style={{
                      position: "absolute",
                      bottom: "0.4rem",
                      right: "0.4rem",
                      background: "transparent",
                      border: "none",
                      color: "var(--text-muted)",
                      fontSize: "0.75rem",
                      cursor: "pointer",
                      padding: "2px 5px",
                      borderRadius: "4px",
                      boxShadow: "none",
                      margin: 0,
                      lineHeight: 1,
                    }}
                    title="Delete resume"
                  >
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="3 6 5 6 21 6"/>
                      <path d="M19 6l-1 14H6L5 6"/>
                      <path d="M10 11v6M14 11v6"/>
                      <path d="M9 6V4h6v2"/>
                    </svg>
                  </button>
                  {item.llm_used && (
                    <div
                      style={{
                        display: "inline-flex",
                        alignItems: "center",
                        gap: "0.35rem",
                        marginTop: "0.35rem",
                        padding: "2px 8px",
                        fontSize: "0.72rem",
                        background: "rgba(74, 222, 128, 0.1)",
                        color: "var(--accent-green)",
                        border: "1px solid rgba(74, 222, 128, 0.2)",
                        borderRadius: "99px",
                      }}
                    >
                      <span style={{ width: "6px", height: "6px", borderRadius: "99px", background: "var(--accent-green)" }} />
                      LLM summary
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </aside>

        <section className="scan-panel">
          <div className="grid gap-4" style={{ textAlign: "left" }}>
            <label>
              <span style={{ display: "block", marginBottom: "0.35rem", color: "var(--text-secondary)", fontWeight: 600 }}>Select Contributor</span>
              <select value={username} onChange={(e) => {
                setUsername(e.target.value);
                setResumeContent("");
                setResumeId(null);
                setEditContent("");
                setIsEditing(false);
                setError("");
              }}
                className="w-full">
                <option value="">Select contributor</option>
                {contributors.map((name) => <option key={name} value={name}>{name}</option>)}
              </select>
            </label>

            {!hasScannedProjects && (
              <p style={{ margin: 0, color: "var(--text-muted)", fontSize: "0.82rem" }}>
                Please scan a project to generate a resume.
              </p>
            )}

            {isContributorSelected && hasScannedProjects && (
              <fieldset
                style={{
                  border: "1px solid var(--border)",
                  borderRadius: "var(--radius-sm)",
                  padding: "0.8rem",
                  margin: 0,
                }}
              >
                <legend style={{ fontSize: "0.85rem", color: "var(--text-secondary)", fontWeight: 600, padding: "0 0.35rem" }}>
                  Projects to Include
                </legend>

                <div className={`project-list-shell ${isLoadingUserProjects || isProjectsTransitioning ? "is-loading" : "is-ready"}`}>
                  {isLoadingUserProjects && (
                    <div className="grid gap-2" style={{ marginTop: "0.2rem" }}>
                      {[0, 1, 2].map((row) => (
                        <div key={`skeleton-${row}`} className="project-skeleton-row" />
                      ))}
                    </div>
                  )}

                  {!isLoadingUserProjects && userProjects.length === 0 && (
                    <p style={{ margin: 0, color: "var(--text-muted)", fontSize: "0.82rem" }}>
                      No ranked projects found for this contributor.
                    </p>
                  )}

                  {!isLoadingUserProjects && userProjects.length > 0 && (
                    <>
                      <p style={{ margin: "0 0 0.5rem", color: "var(--text-muted)", fontSize: "0.78rem" }}>
                        {includedProjectIds.length} selected
                      </p>
                      <div className="flex flex-wrap gap-3" style={{ marginBottom: "0.75rem" }}>
                        <button type="button" className="secondary" onClick={handleSelectAllProjects}>
                          Select All
                        </button>
                        <button type="button" className="secondary" onClick={handleDeselectAllProjects}>
                          Deselect All
                        </button>
                      </div>
                      <div className="grid gap-2" style={{ maxHeight: "180px", overflowY: "auto", paddingRight: "0.25rem" }}>
                        {userProjects.map((project) => {
                          const projectId = project.id ?? project.project_id;
                          if (projectId == null) return null;
                          const label = project.custom_name || project.display_name || project.name;
                          return (
                            <label key={projectId} className="toggle-row" style={{ margin: 0 }}>
                              <input
                                type="checkbox"
                                checked={includedProjectIds.includes(projectId)}
                                onChange={() => toggleInclude(projectId)}
                              />
                              <span>{label}</span>
                            </label>
                          );
                        })}
                      </div>
                      {includedProjectIds.length === 0 && (
                        <p style={{ margin: 0, color: "var(--accent-red)", fontSize: "0.82rem" }}>
                          Select at least one project to include.
                        </p>
                      )}
                    </>
                  )}
                </div>
              </fieldset>
            )}

            <label
              className="toggle-row"
              onClick={(event) => {
                if (isConfigLoaded && !llmConsentGranted) {
                  event.preventDefault();
                  setShowConsentPanel(true);
                }
              }}
              style={{ cursor: isConfigLoaded && llmConsentGranted ? "pointer" : "not-allowed" }}
            >
              <input
                type="checkbox"
                checked={isConfigLoaded && llmConsentGranted ? llmSummary : false}
                disabled={!isConfigLoaded || !llmConsentGranted}
                onChange={(event) => setLlmSummary(event.target.checked)}
                style={{ cursor: isConfigLoaded && llmConsentGranted ? "pointer" : "not-allowed" }}
              />
              <span>
                Include local Ollama LLM summary (runs on-device, no external data transfer).
                {isConfigLoaded && !llmConsentGranted && (
                  <span style={{ marginLeft: "0.4em", color: "rgba(251, 255, 0, 0.7)", fontSize: "0.85em" }}>
                   <br></br> Enable LLM resume consent in Privacy Settings to use this.
                  </span>
                )}
              </span>
            </label>

            <fieldset
              style={{
                border: "1px solid var(--border)",
                borderRadius: "var(--radius-sm)",
                padding: "0.8rem",
                margin: 0,
              }}
            >
              <legend style={{ fontSize: "0.85rem", color: "var(--text-secondary)", fontWeight: 600, padding: "0 0.35rem" }}>
                Education
              </legend>

              <div className="grid gap-3">
                {education.map((edu, index) => {
                  const isOpen = openIndex === index;
                  const getSummary = (entry) => {
                    const parts = [];

                    if (entry.school) parts.push(entry.school);

                    const degreeField = [entry.degree, entry.field].filter(Boolean).join(" ");
                    if (degreeField) parts.push(degreeField);

                    if (entry.start || entry.end) {
                      parts.push(`(${entry.start || ""}-${entry.end || ""})`);
                    }

                    return parts.join(" — ") || "New Education";
                  };

                  const summary = getSummary(edu);
                  const displaySummary = summary;

                  return (
                    <div
                      key={`edu-${index}`}
                      style={{
                        border: "1px solid var(--border)",
                        borderRadius: "var(--radius-sm)",
                        overflow: "hidden",
                        background: "var(--bg-surface)",
                        transition: "all 0.18s ease",
                      }}
                    >
                      <div
                        onClick={() => setOpenIndex(isOpen ? null : index)}
                        role="button"
                        tabIndex={0}
                        onKeyDown={(event) => {
                          if (event.key === "Enter" || event.key === " ") {
                            event.preventDefault();
                            setOpenIndex(isOpen ? null : index);
                          }
                        }}
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                          gap: "0.6rem",
                          padding: "0.7rem 0.8rem",
                          cursor: "pointer",
                          background: isOpen
                            ? "rgba(74, 222, 128, 0.08)"
                            : "var(--bg-surface-md)",
                          boxShadow: isOpen
                            ? "0 0 0 1px rgba(74, 222, 128, 0.2)"
                            : "none",
                          borderBottom: isOpen ? "1px solid var(--border)" : "none",
                          transition: "all 0.18s ease",
                        }}
                      >
                        <div
                          style={{
                            color: "var(--text-secondary)",
                            fontSize: "0.82rem",
                            whiteSpace: "nowrap",
                            overflow: "hidden",
                            textOverflow: "ellipsis",
                          }}
                          title={summary}
                        >
                          {displaySummary}
                        </div>
                        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", flexShrink: 0 }}>
                          {education.length > 1 && (
                            <button
                              type="button"
                              onClick={(event) => {
                                event.stopPropagation();
                                removeEducation(index);
                              }}
                              style={{
                                background: "rgba(248, 113, 113, 0.08)",
                                border: "1px solid rgba(248, 113, 113, 0.2)",
                                color: "rgba(248, 113, 113, 0.9)",
                                cursor: "pointer",
                                fontSize: "0.75rem",
                                padding: "2px 6px",
                                borderRadius: "4px",
                                lineHeight: 1.2,
                                whiteSpace: "nowrap",
                                transition: "all 0.15s ease",
                              }}
                              onMouseEnter={(e) => {
                                e.currentTarget.style.background = "rgba(248,113,113,0.18)";
                              }}
                              onMouseLeave={(e) => {
                                e.currentTarget.style.background = "rgba(248,113,113,0.08)";
                              }}
                              title="Remove education entry"
                            >
                              Remove
                            </button>
                          )}
                          <span style={{ color: "var(--text-muted)", fontSize: "0.78rem" }}>
                            {isOpen ? "▾" : "▸"}
                          </span>
                        </div>
                      </div>

                      {isOpen && (
                        <div className="grid gap-2" style={{ padding: "0.7rem" }}>
                          <input
                            type="text"
                            placeholder="School or University"
                            value={edu.school}
                            onChange={(e) => handleEducationChange(index, "school", e.target.value)}
                          />
                          <input
                            type="text"
                            placeholder="Degree (e.g., BSc, MSc, Diploma)"
                            value={edu.degree}
                            onChange={(e) => handleEducationChange(index, "degree", e.target.value)}
                          />
                          <input
                            type="text"
                            placeholder="Field (e.g., Computer Science)"
                            value={edu.field}
                            onChange={(e) => handleEducationChange(index, "field", e.target.value)}
                          />
                          <input
                            type="text"
                            placeholder="Start (e.g., Sep 2022)"
                            value={edu.start}
                            onChange={(e) => handleEducationChange(index, "start", e.target.value)}
                          />
                          <input
                            type="text"
                            placeholder="End (e.g., May 2026)"
                            value={edu.end}
                            onChange={(e) => handleEducationChange(index, "end", e.target.value)}
                          />
                          <input
                            type="text"
                            placeholder="GPA (optional, e.g., 3.7/4.0)"
                            value={edu.gpa}
                            onChange={(e) => handleEducationChange(index, "gpa", e.target.value)}
                          />
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>

              <button
                type="button"
                className="secondary px-3 py-1"
                style={{ marginTop: "0.7rem" }}
                onClick={addEducation}
              >
                + Add Education
              </button>
            </fieldset>

            <div className="flex flex-wrap gap-3">
              <button onClick={handleGenerateResume} disabled={!canGenerate}
                className="flex items-center gap-2 px-4 py-2">
                {isLoading
                  ? <><span className="inline-block h-3.5 w-3.5 animate-spin rounded-full border-2 border-current border-t-transparent" />Generating…</>
                  : "✦ Generate Resume"}
              </button>
              <button onClick={onBack} className="secondary px-4 py-2">
                ← Back
              </button>
            </div>
          </div>

          {error && (
            <div
              className="flex items-start gap-2 mt-4 px-4 py-3"
              style={{
                borderRadius: "var(--radius-sm)",
                border: "1px solid rgba(248, 113, 113, 0.35)",
                background: "rgba(248, 113, 113, 0.12)",
                color: "var(--accent-red)",
                fontSize: "0.88rem",
              }}
            >
              <span>⚠</span><span>{error}</span>
            </div>
          )}

          {!isLoading && !resumeContent && !error && (
            <p style={{ marginTop: "2rem", textAlign: "center", color: "var(--text-muted)", fontSize: "0.78rem" }}>
              Select a contributor and click Generate to build a resume.
            </p>
          )}

          {resumeContent && (
            <div
              className="mt-8 p-6"
              style={{
                borderRadius: "var(--radius-lg)",
                border: "1px solid rgba(74,222,128,0.2)",
                background: "var(--bg-surface)",
                textAlign: "left",
              }}
            >
              <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                  <span
                    style={{
                      fontSize: "0.72rem",
                      fontWeight: 700,
                      letterSpacing: "0.08em",
                      textTransform: "uppercase",
                      color: "var(--accent-green)",
                    }}
                  >
                    Generated Resume
                  </span>
                  {resumeId && (
                    <span
                      style={{
                        borderRadius: "5px",
                        background: "var(--bg-surface-md)",
                        padding: "2px 7px",
                        fontFamily: "DM Mono, monospace",
                        fontSize: "0.74rem",
                        color: "var(--text-secondary)",
                        border: "1px solid var(--border)",
                      }}
                    >
                      #{resumeId}
                    </span>
                  )}
                </div>
                <div className="flex gap-2">
                  <button onClick={() => { setIsEditing(!isEditing); setEditContent(resumeContent); }}
                    className="secondary px-3 py-1">
                    {isEditing ? "Cancel" : "✏ Edit"}
                  </button>
                  <button onClick={handleCopy}
                    className="secondary px-3 py-1">
                    {copied ? "✓ Copied" : "⎘ Copy"}
                  </button>
                  <button onClick={downloadResume} className="secondary px-3 py-1">
                    ↓ .md
                  </button>
                  <button onClick={downloadTxt} className="secondary px-3 py-1">
                    ↓ .txt
                  </button>
                  <button
                    onClick={downloadPdf}
                    disabled={!resumeId}
                    className="secondary px-3 py-1"
                    style={{
                      background: "rgba(74,222,128,0.08)",
                      borderColor: "rgba(74,222,128,0.25)",
                      color: "var(--accent-green)",
                    }}
                  >
                    ↓ .pdf
                  </button>
                </div>
              </div>

              <div className="mb-4 h-px w-full" style={{ background: "rgba(74, 222, 128, 0.2)" }} />

              {isEditing ? (
                <>
                  <textarea value={editContent} onChange={(e) => setEditContent(e.target.value)}
                    className="w-full p-4"
                    style={{ fontFamily: "DM Mono, monospace", fontSize: "0.86rem" }}
                    rows={20} />
                  <button onClick={handleSaveEdit} disabled={isSaving}
                    className="mt-3 flex items-center gap-2 px-4 py-2">
                    {isSaving
                      ? <><span className="inline-block h-3.5 w-3.5 animate-spin rounded-full border-2 border-current border-t-transparent" />Saving…</>
                      : "Save Changes"}
                  </button>
                </>
              ) : (
                <div
                  className="resume-markdown"
                  style={{
                    background: "rgba(0,0,0,0.2)",
                    border: "1px solid var(--border)",
                    borderRadius: "var(--radius-md)",
                    padding: "1rem",
                    maxHeight: "520px",
                    overflowY: "auto",
                    color: "var(--text-primary)",
                    lineHeight: 1.7,
                  }}
                >
                  <ReactMarkdown>{resumeContent}</ReactMarkdown>
                </div>
              )}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

export default ResumePage;
