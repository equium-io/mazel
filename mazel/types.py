from dataclasses import dataclass
from typing import NewType

# Represents a git commit/pointer
Commit = NewType("Commit", str)


@dataclass
class CommitRange:
    """
    r1..r2 (r2 defaults to HEAD)
    https://git-scm.com/docs/git-rev-parse#_dotted_range_notations
    https://git-scm.com/book/en/v2/Git-Tools-Revision-Selection
    """

    r1: Commit  # "from" commit
    r2: Commit = Commit("HEAD")  # "to" commit

    @classmethod
    def parse(cls, value: str) -> "CommitRange":
        parts = value.split("..")
        if len(parts) == 2:
            r1, r2 = parts
            return CommitRange(r1=Commit(r1), r2=Commit(r2))

        return CommitRange(r1=Commit(parts[0]))
