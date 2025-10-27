-- Drop old tables if they exist
DROP TABLE IF EXISTS files;
DROP TABLE IF EXISTS scans;

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
