from __future__ import annotations

from pathlib import Path
from typing import Union

import tomlkit


class PathableConcept(object):
    def __init__(self, path: Path):
        self.path = path

        # Assume the Workspace's name is the directory name
        # TODO Enforce any name requirements (would they be project-specific
        #   rules)? Allow overriding via config?
        self.name = self.path.name

    def read_toml(
        self, toml_path: Union[str, Path]
    ) -> tomlkit.toml_document.TOMLDocument:
        # TODO Consider caching the result
        return tomlkit.parse(self.read_path(toml_path))

    def read_path(self, path: Union[str, Path]) -> str:
        with open(self.path.joinpath(path)) as f:
            return f.read()

    def path_exists(self, path: Union[str, Path]) -> bool:
        return self.path.joinpath(path).exists()

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {str(self)}>"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.path == other.path

    def __hash__(self) -> int:
        return hash(self.path)
