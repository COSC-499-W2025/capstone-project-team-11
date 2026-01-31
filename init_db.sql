-- Drop dependent tables first
DROP TABLE IF EXISTS file_contributors;
DROP TABLE IF EXISTS file_languages;
DROP TABLE IF EXISTS project_skills;
DROP TABLE IF EXISTS project_evidence;
DROP TABLE IF EXISTS files;
DROP TABLE IF EXISTS resumes;
DROP TABLE IF EXISTS portfolios;
DROP TABLE IF EXISTS scans;

-- Then the parent tables
DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS contributors;
DROP TABLE IF EXISTS languages;
DROP TABLE IF EXISTS skills;

-- Table to store scan history
CREATE TABLE scans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scanned_at TEXT DEFAULT CURRENT_TIMESTAMP,
    project TEXT,
    notes TEXT
);

-- Table to store files and files metadata
CREATE TABLE files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_id INTEGER NOT NULL,
    file_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_extension TEXT,
    file_size INTEGER,
    created_at TEXT,
    modified_at TEXT,
    owner TEXT,
    metadata_json TEXT,  -- stores all other metadata (able to handle all file types)
    FOREIGN KEY (scan_id) REFERENCES scans(id)
);

-- Indexes for faster searching
CREATE INDEX idx_file_path ON files (file_path);
CREATE INDEX idx_file_name ON files (file_name);
CREATE INDEX idx_files_scan_id ON files (scan_id);

-- Projects table to group scans and files under a named project
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    custom_name TEXT,              -- resume display name override
    repo_url TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    thumbnail_path TEXT,
    project_path TEXT,
    git_metrics_json TEXT,
    tech_json TEXT
);


-- Table to store evidence related to projects
CREATE TABLE IF NOT EXISTS project_evidence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    type TEXT NOT NULL,  -- examples: 'metric', 'feedback', 'award', 'link', 'testimonial'
    description TEXT,    -- short label or context
    value TEXT,          -- the actual content, e.g. "10k+ downloads", "Client said: exceeded expectations"
    source TEXT,         -- e.g. "GitHub", "Google Play", "Email", "Internal"
    url TEXT,            -- optional hyperlink
    added_by_user BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Index for faster searching by project_id
CREATE INDEX IF NOT EXISTS idx_project_evidence_project_id ON project_evidence (project_id);

-- Contributors (commit authors). We intentionally do not store emails to keep privacy.
CREATE TABLE IF NOT EXISTS contributors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE
);

-- Languages and skills detected per project
CREATE TABLE IF NOT EXISTS languages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE
);

-- Join tables
CREATE TABLE IF NOT EXISTS file_contributors (
    file_id INTEGER NOT NULL,
    contributor_id INTEGER NOT NULL,
    PRIMARY KEY (file_id, contributor_id),
    FOREIGN KEY (file_id) REFERENCES files(id),
    FOREIGN KEY (contributor_id) REFERENCES contributors(id)
);

CREATE TABLE IF NOT EXISTS file_languages (
    file_id INTEGER NOT NULL,
    language_id INTEGER NOT NULL,
    PRIMARY KEY (file_id, language_id),
    FOREIGN KEY (file_id) REFERENCES files(id),
    FOREIGN KEY (language_id) REFERENCES languages(id)
);

CREATE TABLE IF NOT EXISTS project_skills (
    project_id INTEGER NOT NULL,
    skill_id INTEGER NOT NULL,
    PRIMARY KEY (project_id, skill_id),
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (skill_id) REFERENCES skills(id)
);

-- Generated resumes linked to contributors
CREATE TABLE IF NOT EXISTS resumes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contributor_id INTEGER,
    username TEXT NOT NULL,
    resume_path TEXT NOT NULL,
    metadata_json TEXT,
    generated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (contributor_id) REFERENCES contributors(id)
);

CREATE INDEX IF NOT EXISTS idx_resumes_username ON resumes (username);
CREATE INDEX IF NOT EXISTS idx_resumes_generated_at ON resumes (generated_at);

-- Generated portfolios linked to contributors
CREATE TABLE IF NOT EXISTS portfolios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contributor_id INTEGER,
    username TEXT NOT NULL,
    portfolio_path TEXT NOT NULL,
    metadata_json TEXT,
    generated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (contributor_id) REFERENCES contributors(id)
);

CREATE INDEX IF NOT EXISTS idx_portfolios_username ON portfolios (username);
CREATE INDEX IF NOT EXISTS idx_portfolios_generated_at ON portfolios (generated_at);

-- Helpful indexes
CREATE INDEX IF NOT EXISTS idx_projects_name ON projects (name);
CREATE INDEX IF NOT EXISTS idx_contributors_name ON contributors (name);
CREATE INDEX IF NOT EXISTS idx_languages_name ON languages (name);
CREATE INDEX IF NOT EXISTS idx_skills_name ON skills (name);
