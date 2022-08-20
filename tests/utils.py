from pathlib import Path

from mazel.workspace import Workspace


def abspath(*args) -> Path:
    """Absolute path to the mazel/tests directory"""
    return Path(__file__).parent.joinpath(*args).resolve()


def example_workspace() -> Workspace:
    return Workspace(abspath("examples/simple_workspace"))
