import React, { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";

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
  const [showConsentPanel, setShowConsentPanel] = useState(false);

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
    try {
      const gen = await fetch("http://127.0.0.1:8000/resume/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: selectedUsername, save_to_db: true, llm_summary: llmSummary }),
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

  const downloadPdf = () => {
    const iframe = document.createElement("iframe");
    iframe.style.position = "fixed";
    iframe.style.right = "0";
    iframe.style.bottom = "0";
    iframe.style.width = "0";
    iframe.style.height = "0";
    iframe.style.border = "0";
    iframe.setAttribute("aria-hidden", "true");
    document.body.appendChild(iframe);

    const doc = iframe.contentWindow?.document;
    if (!doc) {
      document.body.removeChild(iframe);
      return;
    }

    const escaped = resumeContent
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");

    doc.open();
    doc.write(
      `<html><head><title>resume_${selectedUsername}.pdf</title></head><body style="margin:24px;color:#0f172a;font-family:'DM Sans',sans-serif;"><pre style="white-space:pre-wrap;font-family:'DM Mono',Consolas,monospace;font-size:12px;line-height:1.45;">${escaped}</pre></body></html>`
    );
    doc.close();

    setTimeout(() => {
      iframe.contentWindow?.focus();
      iframe.contentWindow?.print();
      setTimeout(() => {
        if (iframe.parentNode) iframe.parentNode.removeChild(iframe);
      }, 1200);
    }, 250);
  };

  const requestLlmConsent = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/privacy-consent", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ data_consent: true, llm_resume_consent: true }),
      });
      if (!response.ok) throw new Error("Failed to save consent.");
      setLlmConsentGranted(true);
      setShowConsentPanel(false);
      setLlmSummary(true);
      setError("");
    } catch (err) {
      setError(err.message || "Failed to update consent.");
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
                onChange={(event) => {
                  if (!llmConsentGranted) {
                    setShowConsentPanel(true);
                    return;
                  }
                  setLlmSummary(event.target.checked);
                }}
                style={{ cursor: llmConsentGranted ? "pointer" : "not-allowed" }}
              />
              <span>Include local Ollama LLM summary (runs on-device, no external data transfer).</span>
            </label>

            {showConsentPanel && !llmConsentGranted && (
              <div className="portfolio-notice">
                <p style={{ margin: 0 }}>
                  LLM resume summaries use a local Ollama model and do not send your data to external services.
                </p>
                <div className="flex gap-2 mt-2">
                  <button onClick={requestLlmConsent}>Grant consent</button>
                  <button className="secondary" onClick={() => setShowConsentPanel(false)}>Not now</button>
                </div>
              </div>
            )}

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
