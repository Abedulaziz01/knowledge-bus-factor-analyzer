import subprocess
import shutil
import tempfile
from pathlib import Path

# Where the throwaway repo gets built. tempfile.gettempdir() resolves
# to /tmp on Mac/Linux, and to something like C:\Users\you\AppData\Local\Temp on Windows.
FIXTURE_DIR = Path(tempfile.gettempdir()) / "kbfa_fixture_repo"

ALICE = ("Alice", "alice@example.com")
BOB = ("Bob", "bob@example.com")
CAROL = ("Carol", "carol@example.com")


def run_git(args, author=None):
    """Run a git command inside FIXTURE_DIR, optionally as a specific fake author."""
    cmd = ["git"]
    if author:
        name, email = author
        cmd += ["-c", f"user.name={name}", "-c", f"user.email={email}"]
    cmd += args
    result = subprocess.run(cmd, cwd=FIXTURE_DIR, capture_output=True, text=True)
    if result.returncode != 0:
        print("GIT COMMAND FAILED:", cmd)
        print(result.stderr)
        raise RuntimeError(f"git command failed: {' '.join(cmd)}")


def reset_fixture_dir():
    """Wipe and recreate the fixture folder so this script is safe to re-run."""
    if FIXTURE_DIR.exists():
        shutil.rmtree(FIXTURE_DIR)
    FIXTURE_DIR.mkdir(parents=True)


def commit_file(filename, lines, author, message):
    """Append lines to a file and commit them under a specific fake author."""
    filepath = FIXTURE_DIR / filename
    with open(filepath, "a") as f:
        for line in lines:
            f.write(line + "\n")
    run_git(["add", filename])
    run_git(["commit", "-m", message], author=author)


def build():
    reset_fixture_dir()
    run_git(["init", "-b", "main"])

    # --- auth.py: 95% Alice, 5% Bob -> should score as HIGH risk ---
    alice_lines = [f"# alice line {i}" for i in range(1, 20)]   # 19 lines
    commit_file("auth.py", alice_lines, ALICE, "Alice: initial auth logic")

    bob_lines = ["# bob line 1"]                                 # 1 line
    commit_file("auth.py", bob_lines, BOB, "Bob: small fix to auth")

    # --- utils.py: split evenly 3 ways -> should score as LOW risk ---
    alice_utils = [f"# alice util {i}" for i in range(1, 4)]     # 3 lines
    commit_file("utils.py", alice_utils, ALICE, "Alice: utils part 1")

    bob_utils = [f"# bob util {i}" for i in range(1, 4)]         # 3 lines
    commit_file("utils.py", bob_utils, BOB, "Bob: utils part 2")

    carol_utils = [f"# carol util {i}" for i in range(1, 4)]     # 3 lines
    commit_file("utils.py", carol_utils, CAROL, "Carol: utils part 3")

    print(f"\nFixture repo built at: {FIXTURE_DIR}\n")
    print("Expected ownership (ground truth):")
    print("  auth.py  -> Alice 19/20 = 95%, Bob 1/20 = 5%   -> HIGH risk")
    print("  utils.py -> Alice/Bob/Carol 3/9 = 33% each      -> LOW risk")


if __name__ == "__main__":
    build()