import React, { useEffect, useState } from "react";
import axios from "axios";
import { API_BASE_URL } from "./api";
import { showModal } from "./modal";

function DatabaseMaintenance({ onBack }) {
  const [data, setData] = useState({});
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState({});

  useEffect(() => {
    inspectDatabase();
  }, []);

  const groupSkills = (skillsData = []) => {
    const map = {};
    skillsData.forEach(({ skill, project }) => {
      if (!map[skill]) map[skill] = new Set();
      if (project) map[skill].add(project);
    });
    return map;
  };

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

  if (loading) return <p style={{ padding: 20 }}>Loading database...</p>;

  return (
    <div className="page-shell database-page">
      <header className="app-header">
        <h1>Database Management</h1>
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
        <section className="scan-log-panel" style={{ minWidth: 0 }}>
          
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

          <Section title="Resumes" expanded={expanded.resumes} onToggle={() => toggle("resumes")}>
            <Table
              columns={["ID", "Username", "Path", "Generated"]}
              rows={data.resumes?.map(r => [
                r.id,
                r.username,
                r.resume_path,
                r.generated_at
              ])}
            />
          </Section>

          <Section title="Portfolios" expanded={expanded.portfolios} onToggle={() => toggle("portfolios")}>
            <Table
              columns={["ID", "Username", "Name", "Display Name", "Created"]}
              rows={data.portfolios?.map(p => [
                p.id,
                p.username,
                p.portfolio_name,
                p.display_name || "-",
                p.created_at
              ])}
            />
          </Section>

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

          <Section title="Contributors" expanded={expanded.contributors} onToggle={() => toggle("contributors")}>
            <Table
              columns={["Name"]}
              rows={data.contributors?.map(c => [c.name])}
            />
          </Section>

          <Section title="Languages" expanded={expanded.languages} onToggle={() => toggle("languages")}>
            <Table
              columns={["Language", "File Count"]}
              rows={data.languages?.map(l => [
                l.name,
                l.file_count
              ])}
            />
          </Section>

          <Section title="Project Summaries" expanded={expanded.project_summaries} onToggle={() => toggle("project_summaries")}>
            <Table
              columns={["Project", "Summary"]}
              rows={data.project_summaries?.map(p => [
                p.project,
                p.summary
              ])}
            />
          </Section>

          <Section title="Skills" expanded={expanded.skills} onToggle={() => toggle("skills")}>
            <Table
              columns={["Skill", "Projects"]}
              rows={Object.entries(groupSkills(data.skills_exercised)).map(
                ([skill, projects]) => [
                  skill,
                  Array.from(projects).join(", ")
                ]
              )}
            />
          </Section>

        </section>
      </div>
    </div>
  );
}

/* -------------------------
   Section Component (UPDATED STYLE)
------------------------- */
function Section({ title, expanded, onToggle, children }) {
  return (
    <div
      className="summary-card"
      style={{
        marginTop: 20,
        width: "100%",
        maxWidth: "100%",
        overflow: "hidden",
      }}
    >
      <button onClick={onToggle} style={toggleStyle(expanded)}>
        <span>{title}</span>
        <span style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
          {expanded ? "▾" : "▸"}
        </span>
      </button>

      {expanded && (
        <div style={{ marginTop: 10 }}>
          {children}
        </div>
      )}
    </div>
  );
}

/* -------------------------
   Table Component
------------------------- */
function Table({ columns = [], rows = [] }) {
  if (!rows || rows.length === 0) return <p>No data</p>;

  return (
    <div
      style={{
        width: "100%",
        maxWidth: "100%",
        overflowX: "auto",
        overflowY: "hidden",
      }}
    >
      <table
        className="rank-table"
        style={{
          minWidth: "max-content",
        }}
      >
        <thead>
          <tr>
            {columns.map(col => <th key={col}>{col}</th>)}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i}>
              {row.map((cell, j) => (
                <td key={j}>{cell}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/* -------------------------
   NEW THEMED DROPDOWN STYLE
------------------------- */
const toggleStyle = () => ({
  width: "100%",
  textAlign: "left",
  fontWeight: 600,
  padding: "0.7rem 0.8rem",
  borderRadius: "var(--radius-sm)",
  cursor: "pointer",

  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",

  background: "rgba(74, 222, 128, 0.08)",
  color: "var(--text-secondary)",
  border: "1px solid rgba(74, 222, 128, 0.25)",
  boxShadow: "0 0 0 1px rgba(74, 222, 128, 0.2)",

  transition: "all 0.18s ease",
});

export default DatabaseMaintenance;