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
  const [llmSummary, setLlmSummary] = useState(false);
  const [resumeHistory, setResumeHistory] = useState([]);
  const [deletingId, setDeletingId] = useState(null);
  const [allProjects, setAllProjects] = useState([]);
  const [userProjects, setUserProjects] = useState([]);
  const [excludedProjectIds, setExcludedProjectIds] = useState([]);
  const [isLoadingUserProjects, setIsLoadingUserProjects] = useState(false);

  const selectedUsername = username.trim() || "local";

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
    if (!username.trim()) {
      setUserProjects([]);
      setExcludedProjectIds([]);
      setIsLoadingUserProjects(false);
      return;
    }

    setIsLoadingUserProjects(true);
    setExcludedProjectIds([]);

    fetch(`http://127.0.0.1:8000/rank-projects?mode=contributor&contributor_name=${encodeURIComponent(username.trim())}`)
      .then((r) => r.ok ? r.json() : Promise.reject())
      .then((ranked) => {
        const rankedNames = new Set((Array.isArray(ranked) ? ranked : []).map((item) => item.project));
        setUserProjects(allProjects.filter((project) => rankedNames.has(project.name)));
      })
      .catch(() => {
        setUserProjects([]);
      })
      .finally(() => {
        setIsLoadingUserProjects(false);
      });
  }, [username, allProjects]);

  const toggleExclude = (id) => {
    setExcludedProjectIds((prev) => (
      prev.includes(id)
        ? prev.filter((item) => item !== id)
        : [...prev, id]
    ));
  };

  const handleSelectAllProjects = () => {
    setExcludedProjectIds([]);
  };

  const handleDeselectAllProjects = () => {
    setExcludedProjectIds(
      userProjects
        .map((project) => project.id ?? project.project_id)
        .filter((projectId) => projectId != null)
    );
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

    const excludedProjectNames = excludedProjectIds
      .map((id) => userProjects.find((p) => (p.id ?? p.project_id) === id)?.name)
      .filter(Boolean);

    try {
      const gen = await fetch("http://127.0.0.1:8000/resume/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: selectedUsername,
          save_to_db: true,
          llm_summary: llmSummary,
          excluded_project_names: excludedProjectNames,
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
      fetchHistory(username.trim() || "local");
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

    // Replace window.confirm with showModal
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
    Object.assign(document.createElement("a"), { href: url, download: `resume_${selectedUsername}.md` }).click();
    URL.revokeObjectURL(url);
  };

  const downloadTxt = () => {
    const plainText = resumeContent
      .replace(/^#{1,6}\s*/gm, "")
      .replace(/\*\*/g, "")
      .replace(/^\s*[-*]\s+/gm, "");
    const blob = new Blob([plainText], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    Object.assign(document.createElement("a"), { href: url, download: `resume_${selectedUsername}.txt` }).click();
    URL.revokeObjectURL(url);
  };

  const downloadPdf = async () => {
    setError("");
    if (!resumeId) {
      setError("Select or generate a saved resume before downloading PDF.");
      return;
    }

    try {
      const response = await fetch(`http://127.0.0.1:8000/resume/${resumeId}/pdf`);
      if (!response.ok) {
        const { detail } = await response.json().catch(() => ({}));
        throw new Error(detail || "Failed to generate PDF.");
      }

      const blob = await response.blob();
      const contentDisposition = response.headers.get("Content-Disposition") || "";
      const filenameMatch = contentDisposition.match(/filename="?([^";]+)"?/i);
      const filename = filenameMatch?.[1] || `resume_${selectedUsername}.pdf`;

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
                    <span className="recent-title" style={{ margin: 0 }}>{item.username || "local"}</span>
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
              }}
                className="w-full">
                <option value="">No git username (local/guest)</option>
                {contributors.map((name) => <option key={name} value={name}>{name}</option>)}
              </select>
            </label>

            {username.trim() && (
              <fieldset
                style={{
                  border: "1px solid var(--border)",
                  borderRadius: "var(--radius-sm)",
                  padding: "0.8rem",
                  margin: 0,
                }}
              >
                <legend style={{ fontSize: "0.85rem", color: "var(--text-secondary)", fontWeight: 600, padding: "0 0.35rem" }}>
                  Exclude Projects from Resume
                </legend>

                {isLoadingUserProjects && (
                  <p style={{ margin: 0, color: "var(--text-muted)", fontSize: "0.82rem" }}>
                    Loading contributor projects...
                  </p>
                )}

                {!isLoadingUserProjects && userProjects.length === 0 && (
                  <p style={{ margin: 0, color: "var(--text-muted)", fontSize: "0.82rem" }}>
                    No ranked projects found for this contributor.
                  </p>
                )}

                {!isLoadingUserProjects && userProjects.length > 0 && (
                  <>
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
                              checked={!excludedProjectIds.includes(projectId)}
                              onChange={() => toggleExclude(projectId)}
                            />
                            <span>{label}</span>
                          </label>
                        );
                      })}
                    </div>
                  </>
                )}
              </fieldset>
            )}

            <label
              className="toggle-row"
              onClick={(event) => {
                if (!llmConsentGranted) {
                  event.preventDefault();
                  setShowConsentPanel(true);
                }
              }}
              style={{ cursor: llmConsentGranted ? "pointer" : "help" }}
            >
              <input
                type="checkbox"
                checked={llmConsentGranted ? llmSummary : false}
                disabled={!llmConsentGranted}
                onChange={(event) => setLlmSummary(event.target.checked)}
                style={{ cursor: llmConsentGranted ? "pointer" : "not-allowed" }}
              />
              <span>
                Include local Ollama LLM summary (runs on-device, no external data transfer).
                {!llmConsentGranted && (
                  <span style={{ marginLeft: "0.4em", color: "rgba(251, 255, 0, 0.7)", fontSize: "0.85em" }}>
                   <br></br> Enable LLM resume consent in Privacy Settings to use this.
                  </span>
                )}
              </span>
            </label>

            <div className="flex flex-wrap gap-3">
              <button onClick={handleGenerateResume} disabled={isLoading}
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
