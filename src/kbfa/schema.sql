CREATE TABLE IF NOT EXISTS blame_lines (
    file_path  TEXT,
    author     TEXT,
    email      TEXT,
    line_count INTEGER,
    scanned_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS file_ownership (
    file_path   TEXT,
    author      TEXT,
    email       TEXT,
    pct_owned   DOUBLE,
    total_lines INTEGER,
    scanned_at  TIMESTAMP
);