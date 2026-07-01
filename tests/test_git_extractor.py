import os
import tempfile
import pytest
from tests.fixtures.build_fixture_repo import build, FIXTURE_DIR
from src.kbfa.git_extractor import get_blame_records


@pytest.fixture(scope="module")
def fixture_repo():
    """
    Build the fixture repo once for all tests in this file.
    'scope=module' means it only runs once per pytest session,
    not once per individual test — saves time.
    """
    build()
    return str(FIXTURE_DIR)


def get_author_lines(records, filename, author):
    """
    Helper: from the full list of blame records, find the line count
    for a specific (file, author) combination.
    Returns 0 if that author has no lines in that file.
    """
    for record in records:
        if record["file"] == filename and record["author"] == author:
            return record["line_count"]
    return 0


def test_extractor_returns_records(fixture_repo):
    """Smoke test: the extractor should return a non-empty list."""
    records = get_blame_records(fixture_repo)
    assert len(records) > 0, "Expected at least one blame record but got none"


def test_auth_py_alice_owns_19_lines(fixture_repo):
    """
    Ground truth check: auth.py was built with 19 lines from Alice.
    If this fails, the extractor's line counting is broken.
    """
    records = get_blame_records(fixture_repo)
    alice_lines = get_author_lines(records, "auth.py", "Alice")
    assert alice_lines == 19, f"Expected 19 but got {alice_lines}"


def test_auth_py_bob_owns_1_line(fixture_repo):
    """
    Ground truth check: auth.py was built with 1 line from Bob.
    """
    records = get_blame_records(fixture_repo)
    bob_lines = get_author_lines(records, "auth.py", "Bob")
    assert bob_lines == 1, f"Expected 1 but got {bob_lines}"


def test_utils_py_even_split(fixture_repo):
    """
    Ground truth check: utils.py was built with 3 lines each from
    Alice, Bob, and Carol. All three should match.
    """
    records = get_blame_records(fixture_repo)
    for author in ["Alice", "Bob", "Carol"]:
        lines = get_author_lines(records, "utils.py", author)
        assert lines == 3, f"Expected 3 lines for {author} in utils.py but got {lines}"


def test_auth_py_total_lines(fixture_repo):
    """
    Sanity check: auth.py should have exactly 20 lines total (19 + 1).
    If this fails, the extractor is either missing lines or double-counting.
    """
    records = get_blame_records(fixture_repo)
    auth_records = [r for r in records if r["file"] == "auth.py"]
    total = sum(r["line_count"] for r in auth_records)
    assert total == 20, f"Expected 20 total lines in auth.py but got {total}"