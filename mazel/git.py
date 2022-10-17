import subprocess
from pathlib import Path

from .fs import cd
from .types import CommitRange


def git_modified_files(repo_dir: Path, commit_range: CommitRange) -> list[Path]:

    with cd(repo_dir):  # Can technically run anywhere *within* the repo
        # Could use GitPython instead, but we only need to run one command and parse
        # output.
        # If we get more advanced, consider switching over to a proper library.
        cmd = subprocess.run(
            ["git", "diff", "--name-only", commit_range.r1, commit_range.r2],
            capture_output=True,
            text=True,
            check=True,
        )

    return [Path(fn) for fn in cmd.stdout.strip().split("\n")]
