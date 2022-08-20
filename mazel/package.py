from __future__ import annotations

from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, List

import tomlkit

from .base import PathableConcept
from .exceptions import InvalidBuildToml
from .runtimes import Runtime

if TYPE_CHECKING:
    # Avoid circular import for type declarations
    from .workspace import Workspace  # pragma: no cover


class Package(PathableConcept):
    # We could alternatively attempt to discover the package via hints like
    # a Makefile, pyproject.toml, or package.json in the directory, but instead
    # we explicitly use a BUILD.toml file (in some small way trying to keep
    # aligned with bazel's BUILD.bzl).
    BUILD_TOML = "BUILD.toml"

    def __init__(self, path: Path, workspace: Workspace):
        super().__init__(path)
        self.workspace = workspace

    @cached_property
    def build_toml(self) -> tomlkit.toml_document.TOMLDocument:
        return self.read_toml(self.BUILD_TOML)

    @property
    def _build_toml_package(self) -> tomlkit.toml_document.TOMLDocument:
        try:
            return self.build_toml["package"]
        except KeyError:
            raise InvalidBuildToml(f"No [package] section in {self.path}/BUILD.toml")

    @cached_property
    def label_path(self) -> str:
        # The Package.path is a subdir of Workspace.path, so we
        # truncate off the workspace path via Path.relative_to().
        relpath = self.path.relative_to(self.workspace.path)
        return f"//{relpath}"

    def relative_package(self, relative_path: Path) -> "Package":
        """Given a relative file path to this Package, resolve the sibling Package"""
        # TODO validate it is a legal path (e.g. has a BUILD.toml)
        path = self.path.joinpath(relative_path).resolve()
        return self.workspace.get_package(path)

    def runtimes(self) -> List[Runtime]:
        """Return list of Runtimes as defined by package.runtimes in BUILD.toml"""
        labels = self._build_toml_package.get("runtimes")

        if labels is None:
            return []
        elif not isinstance(labels, list):
            labels = [labels]

        return [Runtime.resolve(label, self) for label in labels]

    def depends_on(self) -> List["Package"]:
        """
        Provides the explicit (BUILD.toml's package.depends_on) and
        implicit (pyproject.toml/package.json) intra-workspace dependencies.
        """
        deps = []

        # Dependencies via BUILD.toml package.depends_on
        explicit = self._build_toml_package.get("depends_on")
        if explicit is not None:
            for label_path in explicit:
                deps.append(self.workspace.resolve_label_path(label_path))

        # Dependencies via the Runtime's computed dependencies
        for runtime in self.runtimes():
            for pkg in runtime.workspace_dependencies():
                deps.append(pkg)

        # Deduplicate dependencies.
        # TODO warn on duplicates
        return list(set(deps))
