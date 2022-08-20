from contextlib import contextmanager
from os import chdir
from pathlib import Path
from typing import Generator, Union


# Replicated from equium.common.fs (so we have no dependencies on internal libraries)
@contextmanager
def cd(path: Union[str, Path]) -> Generator[None, None, None]:
    """Unix-like cd as a context manager."""
    original = Path.cwd()

    # Cast to Path, incase we received a str
    chdir(Path(path).expanduser())

    try:
        yield
    finally:
        chdir(original)
