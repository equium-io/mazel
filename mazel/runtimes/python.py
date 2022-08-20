from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Iterable, Optional, Tuple, cast

import tomlkit

from .base import Runtime

if TYPE_CHECKING:
    # Avoid circular import for type declarations
    from mazel.package import Package  # noqa  # pragma: no cover


class PythonRuntime(Runtime):
    runtime_label = "python"

    @cached_property
    def pyproject_toml(self) -> tomlkit.toml_document.TOMLDocument:
        return self.package.read_toml("pyproject.toml")

    def workspace_dependencies(self) -> Iterable["Package"]:
        deps = self.dependencies()
        dev_deps = self.dev_dependencies()

        # Update to copy into a new dict, since self.pyproject_toml caches the toml
        combined = {}
        combined.update(deps)
        combined.update(dev_deps)

        for dep in combined.items():
            pkg = self._as_relative_package(dep)
            if pkg is not None:
                yield pkg

    def dependencies(self) -> Dict[str, Any]:
        return self._retrieve_dependencies("dependencies")

    def dev_dependencies(self) -> Dict[str, Any]:
        return self._retrieve_dependencies("dev-dependencies")

    def _poetry_sections(self) -> Dict[str, Any]:
        return cast(
            Dict[str, Any], self.pyproject_toml.get("tool", {}).get("poetry", {})
        )

    def _retrieve_dependencies(self, section_label: str) -> Dict[str, Any]:
        return self._poetry_sections().get(section_label, {})

    def _as_relative_package(self, dependency: Tuple[str, Any]) -> Optional["Package"]:
        name, version = dependency
        if (
            isinstance(version, dict)
            and "path" in version
            # Assume a relative path is another package in the workspace
            and version["path"].startswith("..")
        ):
            return self.package.relative_package(Path(version["path"]))

        return None
