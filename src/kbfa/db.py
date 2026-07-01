import duckdb
from datetime import datetime, timezone
from pathlib import Path
from src.kbfa.config import DUCKDB_PATH


def get_connection() -> duckdb.DuckDBPyConnection:
    """
    Open (or create) the DuckDB database file at DUCKDB_PATH,
    run schema.sql to ensure tables exist, and return the connection.

    DuckDB works like SQLite — the database is just a single file on disk.
    If the file doesn't exist yet, DuckDB creates it automatically.
    """
    # Make sure the directory exists before DuckDB tries to create the file.
    db_path = Path(DUCKDB_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = duckdb.connect(str(db_path))

    # Run schema.sql every time we connect.
    # IF NOT EXISTS in the SQL means this is safe — it won't
    # drop existing data or error if tables already exist.
    schema_path = Path(__file__).parent / "schema.sql"
    schema_sql = schema_path.read_text()
    # DuckDB has no executescript() — split on semicolons and run each
    # statement individually, skipping any empty strings.
    for statement in schema_sql.split(";"):
        statement = statement.strip()
        if statement:
            conn.execute(statement)

    return conn


def clear_blame_lines(conn: duckdb.DuckDBPyConnection) -> None:
    """
    Delete all existing rows from blame_lines and file_ownership
    before a fresh scan. This prevents duplicate rows if you run
    the extractor twice on the same repo.
    """
    conn.execute("DELETE FROM blame_lines")
    conn.execute("DELETE FROM file_ownership")


def insert_blame_lines(
    conn: duckdb.DuckDBPyConnection,
    records: list[dict]
) -> None:
    """
    Insert blame records from git_extractor into the blame_lines table.

    Each record looks like:
    {"file": "auth.py", "author": "Alice", "email": "alice@example.com", "line_count": 19}

    We add a scanned_at timestamp so you know when the scan happened.
    """
    scanned_at = datetime.now(timezone.utc)

    rows = [
        (
            record["file"],
            record["author"],
            record["email"],
            record["line_count"],
            scanned_at,
        )
        for record in records
    ]

    conn.executemany(
        "INSERT INTO blame_lines (file_path, author, email, line_count, scanned_at) VALUES (?, ?, ?, ?, ?)",
        rows,
    )


def compute_and_store_ownership(conn: duckdb.DuckDBPyConnection) -> None:
    """
    Calculate % ownership per (file, author) from blame_lines and
    store the results in file_ownership.

    The math:
    - total_lines per file = sum of all authors' line_counts for that file
    - pct_owned = (this author's line_count / total_lines) * 100
    """
    conn.execute("""
        INSERT INTO file_ownership (file_path, author, email, pct_owned, total_lines, scanned_at)
        SELECT
            b.file_path,
            b.author,
            b.email,
            ROUND((b.line_count * 100.0) / totals.total_lines, 2) AS pct_owned,
            totals.total_lines,
            b.scanned_at
        FROM blame_lines b
        JOIN (
            SELECT file_path, SUM(line_count) AS total_lines
            FROM blame_lines
            GROUP BY file_path
        ) totals ON b.file_path = totals.file_path
    """)


def query_df(conn: duckdb.DuckDBPyConnection, sql: str):
    """
    Run any SQL query and return the result as a pandas DataFrame.
    Useful for quick inspection and for the dashboard later.
    """
    return conn.execute(sql).df()