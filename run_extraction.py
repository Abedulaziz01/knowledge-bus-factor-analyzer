import os
import tempfile
from tests.fixtures.build_fixture_repo import build, FIXTURE_DIR
from src.kbfa.git_extractor import get_blame_records
from src.kbfa.db import get_connection, clear_blame_lines, insert_blame_lines, compute_and_store_ownership, query_df

# Step 1: Make sure the fixture repo exists
print("Building fixture repo...")
build()

# Step 2: Extract blame records from it
print("Running git blame extraction...")
records = get_blame_records(str(FIXTURE_DIR))
print(f"  Found {len(records)} blame records")

# Step 3: Store in DuckDB
print("Storing in DuckDB...")
conn = get_connection()
clear_blame_lines(conn)
insert_blame_lines(conn, records)
compute_and_store_ownership(conn)

# Step 4: Query and display results
print("\n--- blame_lines table ---")
print(query_df(conn, "SELECT * FROM blame_lines"))

print("\n--- file_ownership table ---")
print(query_df(conn, "SELECT * FROM file_ownership ORDER BY file_path, pct_owned DESC"))

conn.close()
print("\nDone.")