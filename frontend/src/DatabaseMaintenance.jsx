import React, { useEffect, useState } from "react";
import axios from "axios";
import { API_BASE_URL } from "./api";
import { showModal } from "./modal";

function DatabaseMaintenance({ onBack }) {
  const [data, setData] = useState({});
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState({
    projects: true, // default open
  });

  useEffect(() => {
    inspectDatabase();
  }, []);

  const inspectDatabase = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_BASE_URL}/database/inspect`);
      setData(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const clearDatabase = async () => {
    const confirmed = await showModal({
      type: "danger",
      title: "Clear Database",
      message: `Are you sure you want to delete all database data?<br/><strong>This cannot be undone.</strong>`,
      confirmText: "Yes, Clear",
      cancelText: "Cancel",
    });

    if (!confirmed) return;

    try {
      await axios.delete(`${API_BASE_URL}/database/clear`);
      inspectDatabase();
    } catch (err) {
      console.error(err);
    }
  };

  const toggle = (key) => {
    setExpanded((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  // -------------------------
  // Stats (NO FILES)
  // -------------------------
  const stats = {
    projects: data.projects?.length || 0,
    scans: data.recent_scans?.length || 0,
    contributors: data.contributors?.length || 0,
    languages: data.languages?.length || 0,
  };

  if (loading) return <p style={{ padding: 20 }}>Loading database...</p>;

  return (
    <div className="page-shell database-page">
      <header className="app-header">
        <h1>Database Dashboard</h1>
        <p>Overview of your scanned projects and activity.</p>
      </header>

      <div className="scan-layout">
        {/* LEFT PANEL */}
        <section className="scan-panel">
          <h2>Database Tools</h2>
          <button onClick={inspectDatabase}>Refresh Database</button>
          <button className="danger" onClick={clearDatabase}>
            Clear Database
          </button>
          <button className="secondary" onClick={onBack}>
            Back to Main Menu
          </button>
        </section>

        {/* RIGHT PANEL */}
        <section className="scan-log-panel">
          {/* ---------------- PROJECTS ---------------- */}
          <Section title="Projects" expanded={expanded.projects} onToggle={() => toggle("projects")}>
            <Table
              columns={["Name", "Scans", "Files", "Skills"]}
              rows={data.projects?.map(p => [
                p.name,
                p.scan_count,
                p.file_count,
                (p.skills || []).join(", ")
              ])}
            />
          </Section>

          {/* ---------------- SCANS ---------------- */}
          <Section title="Recent Scans" expanded={expanded.scans} onToggle={() => toggle("scans")}>
            <Table
              columns={["ID", "Project", "Date", "Notes"]}
              rows={data.recent_scans?.map(s => [
                s.id,
                s.project,
                s.scanned_at,
                s.notes || "-"
              ])}
            />
          </Section>

          {/* ---------------- CONTRIBUTORS ---------------- */}
          <Section title="Contributors" expanded={expanded.contributors} onToggle={() => toggle("contributors")}>
            <Table
              columns={["ID", "Name"]}
              rows={data.contributors?.map(c => [
                c.id,
                c.name
              ])}
            />
          </Section>

          {/* ---------------- LANGUAGES ---------------- */}
          <Section title="Languages" expanded={expanded.languages} onToggle={() => toggle("languages")}>
            <Table
              columns={["Language", "File Count"]}
              rows={data.languages?.map(l => [
                l.name,
                l.file_count
              ])}
            />
          </Section>

          {/* ---------------- PROJECT SUMMARIES ---------------- */}
          <Section title="Project Summaries" expanded={expanded.project_summaries} onToggle={() => toggle("project_summaries")}>
            <Table
              columns={["Project", "Summary"]}
              rows={data.project_summaries?.map(p => [
                p.project,
                p.summary
              ])}
            />
          </Section>

          {/* ---------------- SKILLS TIMELINE ---------------- */}
          <Section title="Skills Exercised" expanded={expanded.skills} onToggle={() => toggle("skills")}>
            <Table
              columns={["Skill", "Date", "Project"]}
              rows={data.skills_exercised?.map(s => [
                s.skill,
                s.datetime,
                s.project
              ])}
            />
          </Section>

        </section>
      </div>
    </div>
  );
}

/* -------------------------
   Reusable Section Component
------------------------- */
function Section({ title, expanded, onToggle, children }) {
  return (
    <div className="summary-card" style={{ marginTop: 20 }}>
      <button onClick={onToggle} style={toggleStyle}>
        {expanded ? "▼" : "▶"} {title}
      </button>
      {expanded && <div style={{ marginTop: 10 }}>{children}</div>}
    </div>
  );
}

/* -------------------------
   Reusable Table Component
------------------------- */
function Table({ columns = [], rows = [] }) {
  if (!rows || rows.length === 0) return <p>No data</p>;

  return (
    <table className="rank-table">
      <thead>
        <tr>
          {columns.map(col => <th key={col}>{col}</th>)}
        </tr>
      </thead>
      <tbody>
        {rows.map((row, i) => (
          <tr key={i}>
            {row.map((cell, j) => (
              <td key={j}>
                {typeof cell === "string" && cell.length > 80
                  ? cell.substring(0, 80) + "..."
                  : cell}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

/* -------------------------
   Styles
------------------------- */
const toggleStyle = {
  width: "100%",
  textAlign: "left",
  fontWeight: 700,
  background: "#edf6e6",
  color: "#2a4e2a",
  border: "1px solid #d7e4cf",
  padding: "6px 10px",
  borderRadius: 6,
};

export default DatabaseMaintenance;