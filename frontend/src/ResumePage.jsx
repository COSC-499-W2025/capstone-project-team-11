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

  useEffect(() => {
    fetch("http://127.0.0.1:8000/contributors")
      .then((r) => r.ok ? r.json() : Promise.reject())
      .then(setContributors)
      .catch(() => console.error("Contributor fetch failed"));
  }, []);

  const handleGenerateResume = async () => {
    setError(""); setResumeContent(""); setResumeId(null); setIsLoading(true);
    try {
      const gen = await fetch("http://127.0.0.1:8000/resume/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: username.trim() || "local", save_to_db: true, llm_summary: false }),
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
    Object.assign(document.createElement("a"), { href: url, download: `resume_${username || "local"}.md` }).click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="page-shell">
      <header className="app-header">
        <h1>Generate Resume</h1>
        <p>Create a contributor-focused resume from project data.</p>
      </header>

      <div className="scan-layout">
        <section className="scan-panel">
          <div className="space-y-4 text-left">
            <label className="block">
              <span className="mb-1 block text-sm font-medium text-slate-200">Select Contributor</span>
              <select value={username} onChange={(e) => setUsername(e.target.value)}
                className="w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100 outline-none focus:ring-2 focus:ring-emerald-500">
                <option value="">No git username (local/guest)</option>
                {contributors.map((name) => <option key={name} value={name}>{name}</option>)}
              </select>
            </label>

            <div className="flex flex-wrap gap-3">
              <button onClick={handleGenerateResume} disabled={isLoading}
                className="flex items-center gap-2 rounded-md border border-emerald-700 bg-emerald-700 px-4 py-2 text-sm font-semibold text-emerald-100 transition hover:bg-emerald-600 disabled:cursor-not-allowed disabled:opacity-60">
                {isLoading
                  ? <><span className="inline-block h-3.5 w-3.5 animate-spin rounded-full border-2 border-emerald-300 border-t-transparent" />Generating…</>
                  : "✦ Generate Resume"}
              </button>
              <button onClick={onBack}
                className="rounded-md border border-slate-700 bg-slate-800 px-4 py-2 text-sm font-semibold text-slate-200 transition hover:bg-slate-700">
                ← Back
              </button>
            </div>
          </div>

          {error && (
            <div className="mt-4 flex items-start gap-2 rounded-md border border-red-700 bg-red-950/40 px-4 py-3 text-sm text-red-200">
              <span className="mt-0.5 text-red-400">⚠</span><span>{error}</span>
            </div>
          )}

          {!isLoading && !resumeContent && !error && (
            <p className="mt-8 text-center text-xs text-slate-600">Select a contributor and click Generate to build a resume.</p>
          )}

          {resumeContent && (
            <div className="mt-8 rounded-lg border border-emerald-900 bg-slate-950/80 p-6 text-left">
              <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                  <span className="text-xs font-semibold uppercase tracking-widest text-emerald-400">Generated Resume</span>
                  {resumeId && <span className="rounded bg-slate-800 px-2 py-0.5 font-mono text-xs text-slate-400">#{resumeId}</span>}
                </div>
                <div className="flex gap-2">
                  <button onClick={() => { setIsEditing(!isEditing); setEditContent(resumeContent); }}
                    className="rounded border border-slate-700 bg-slate-800 px-3 py-1 text-xs font-semibold text-slate-300 transition hover:bg-slate-700">
                    {isEditing ? "Cancel" : "✏ Edit"}
                  </button>
                  <button onClick={handleCopy}
                    className="rounded border border-slate-700 bg-slate-800 px-3 py-1 text-xs font-semibold text-slate-300 transition hover:bg-slate-700">
                    {copied ? "✓ Copied" : "⎘ Copy"}
                  </button>
                  <button onClick={downloadResume}
                    className="rounded border border-emerald-800 bg-emerald-900/50 px-3 py-1 text-xs font-semibold text-emerald-300 transition hover:bg-emerald-800">
                    ↓ Download
                  </button>
                </div>
              </div>

              <div className="mb-4 h-px w-full bg-emerald-900/50" />

              {isEditing ? (
                <>
                  <textarea value={editContent} onChange={(e) => setEditContent(e.target.value)}
                    className="w-full rounded-md border border-slate-700 bg-slate-900 p-4 font-mono text-sm text-slate-100 outline-none focus:ring-2 focus:ring-emerald-500"
                    rows={20} />
                  <button onClick={handleSaveEdit} disabled={isSaving}
                    className="mt-3 flex items-center gap-2 rounded-md border border-emerald-700 bg-emerald-700 px-4 py-2 text-sm font-semibold text-emerald-100 transition hover:bg-emerald-600 disabled:opacity-60">
                    {isSaving
                      ? <><span className="inline-block h-3.5 w-3.5 animate-spin rounded-full border-2 border-emerald-300 border-t-transparent" />Saving…</>
                      : "Save Changes"}
                  </button>
                </>
              ) : (
                <div className="prose prose-invert max-w-none leading-relaxed text-slate-100">
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