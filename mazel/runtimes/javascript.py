import json
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Iterable, Optional, Tuple, cast

from .base import Runtime

if TYPE_CHECKING:
    # Avoid circular import for type declarations
    from mazel.package import Package  # noqa  # pragma: no cover


class JavascriptRuntime(Runtime):
    runtime_label = "javascript"

    @cached_property
    def package_json(self) -> Dict[str, Any]:
        return cast(Dict[str, Any], json.loads(self.package.read_path("package.json")))

    def workspace_dependencies(self) -> Iterable["Package"]:
        """
        Supports package.json local paths

        https://docs.npmjs.com/files/package.json#local-paths
        """

        # NOTE: copied from mazel.runtimes.python -- perhaps we should refactor, but
        # the dependencies/devDependencies pattern does not seem universal
        deps = self.dependencies()
        dev_deps = self.dev_dependencies()

        combined = {}
        combined.update(deps)
        combined.update(dev_deps)

        for dep in combined.items():
            pkg = self._as_relative_package(dep)
            if pkg is not None:
                yield pkg

    def dependencies(self) -> Dict[str, str]:
        return self._retrieve_dependencies("dependencies")

    def dev_dependencies(self) -> Dict[str, str]:
        return self._retrieve_dependencies("devDependencies")

    def _retrieve_dependencies(self, section_label: str) -> Dict[str, str]:
        return cast(Dict[str, str], self.package_json.get(section_label, {}))

    def _as_relative_package(self, dependency: Tuple[str, str]) -> Optional["Package"]:
        name, version = dependency
        if version.startswith("file:"):
            # Chop off the leading "file:"
            return self.package.relative_package(Path(version[5:]))
        return None
