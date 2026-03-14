import React, { useEffect, useState } from "react";
import axios from "axios";
import { API_BASE_URL } from "./api";

function DatabaseMaintenance({ onBack }) {
  const [tables, setTables] = useState({});
  const [expanded, setExpanded] = useState({});
  const [loading, setLoading] = useState(true);
  const [content, setContent] = useState(null);

  useEffect(() => {
    inspectDatabase();
  }, []);

  const inspectDatabase = async () => {
    setLoading(true);
    setContent(null);

    try {
      const res = await axios.get(`${API_BASE_URL}/database/inspect`);
      const data = res.data;
      const tablesObj = {};

      if (data.recent_scans) {
        tablesObj.recent_scans = {
          columns: ["id", "project", "scanned_at", "notes"],
          rows: data.recent_scans.map(s => [s.id, s.project, s.scanned_at, s.notes]),
          row_count: data.recent_scans.length
        };
      }

      if (data.projects) {
        tablesObj.projects = {
          columns: ["id", "name", "repo_url", "scan_count", "file_count", "skills", "summary_text"],
          rows: data.projects.map(p => [
            p.id,
            p.name,
            p.repo_url,
            p.scan_count,
            p.file_count,
            p.skills.join(", "),
            p.summary_text
          ]),
          row_count: data.projects.length
        };
      }

      if (data.project_summaries) {
        tablesObj.project_summaries = {
          columns: ["project", "summary"],
          rows: data.project_summaries.map(p => [p.project, p.summary || "<none>"]),
          row_count: data.project_summaries.length
        };
      }

      if (data.files) {
        tablesObj.files = {
          columns: ["id", "file_name", "file_extension", "file_size", "modified_at", "file_path", "scan_id"],
          rows: data.files.map(f => [f.id, f.file_name, f.file_extension, f.file_size, f.modified_at, f.file_path, f.scan_id]),
          row_count: data.files.length
        };
      }

      if (data.contributors) {
        tablesObj.contributors = {
          columns: ["id", "name", "sample_files"],
          rows: data.contributors.map(c => [
            c.id,
            c.name,
            c.sample_files.map(sf => sf.file_name).join(", ")
          ]),
          row_count: data.contributors.length
        };
      }

      if (data.languages) {
        tablesObj.languages = {
          columns: ["name", "file_count"],
          rows: data.languages.map(l => [l.name, l.file_count]),
          row_count: data.languages.length
        };
      }

      if (data.thumbnails) {
        tablesObj.thumbnails = {
          columns: ["project_id", "project_name", "thumbnail_path", "status"],
          rows: data.thumbnails.map(t => [t.project_id, t.project_name, t.thumbnail_path, t.status]),
          row_count: data.thumbnails.length
        };
      }

      if (data.skills_exercised) {
        tablesObj.skills_exercised = {
          columns: ["skill", "datetime", "project"],
          rows: data.skills_exercised.map(s => [s.skill, s.datetime, s.project]),
          row_count: data.skills_exercised.length
        };
      }

      if (data.project_skills) {
        tablesObj.project_skills = {
          columns: ["project_id", "skill"],
          rows: data.project_skills.map(ps => [ps.project_id, ps.skill]),
          row_count: data.project_skills.length
        };
      }

      if (data.file_contributors) {
        tablesObj.file_contributors = {
          columns: ["file_id", "contributor_id"],
          rows: data.file_contributors.map(fc => [fc.file_id, fc.contributor_id]),
          row_count: data.file_contributors.length
        };
      }

      setTables(tablesObj);
    } catch (err) {
      console.error(err);
      setContent(<p className="error-text">Failed to inspect database.</p>);
    } finally {
      setLoading(false);
    }
  };

  const toggleTable = (name) => {
    setExpanded(prev => ({ ...prev, [name]: !prev[name] }));
  };

  // modified functions to show "functionality to be added later"
  const clearDatabase = async () => {
    const confirmClear = window.confirm(
      "Are you sure you want to clear the entire database? This cannot be undone."
    );

    if (!confirmClear) return;

    try {
      await axios.delete(`${API_BASE_URL}/database/clear`);

      alert("Database cleared successfully.");

      // reload the tables so UI updates
      inspectDatabase();
    } catch (err) {
      console.error(err);
      alert("Failed to clear database.");
    }
  };

  const renderTables = () => {
    const tableNames = Object.keys(tables);
    if (tableNames.length === 0) return <p>No tables found in database.</p>;

    return tableNames.map(name => {
      const table = tables[name];
      const isOpen = expanded[name];
      const displayColumns = table.columns.slice(0, 10);
      const columnIndexes = displayColumns.map(col => table.columns.indexOf(col));

      return (
        <div key={name} className="summary-card">
          <button
            onClick={() => toggleTable(name)}
            style={{ width: "100%", textAlign: "left", fontWeight: 700, background: "#edf6e6", color: "#2a4e2a", border: "1px solid #d7e4cf" }}
          >
            {isOpen ? "▼" : "▶"} {name} ({table.row_count})
          </button>

          {isOpen && (
            <div className="rank-table-wrap" style={{ marginTop: 10 }}>
              <table className="rank-table">
                <thead>
                  <tr>{displayColumns.map(col => <th key={col}>{col}</th>)}</tr>
                </thead>
                <tbody>
                  {table.rows.length === 0 ? (
                    <tr><td colSpan={displayColumns.length}>No rows</td></tr>
                  ) : (
                    table.rows.map((row, i) => (
                      <tr key={i}>
                        {columnIndexes.map(index => {
                          let value = row[index];
                          if (typeof value === "string" && value.length > 60) value = value.substring(0, 60) + "...";
                          return <td key={index}>{value ?? "NULL"}</td>;
                        })}
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      );
    });
  };

  return (
    <div className="page-shell database-page">
      <header className="app-header">
        <h1>Database Management</h1>
        <p>Inspect stored database tables, remove projects, or clear the database.</p>
      </header>

      <div className="scan-layout">
        <section className="scan-panel">
          <h2>Database Tools</h2>
          <button onClick={inspectDatabase}>Refresh Database</button>
          <button className="danger" onClick={clearDatabase}>Clear Database</button>
          <button className="secondary" onClick={onBack}>Back to Main Menu</button>
        </section>

        <section className="scan-log-panel">
          <h2>Database Tables</h2>
          {loading ? <p>Loading database tables...</p> : renderTables()}
          {content}
        </section>
      </div>
    </div>
  );
}

export default DatabaseMaintenance;