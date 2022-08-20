from __future__ import annotations

from typing import TYPE_CHECKING, List, Mapping, Optional

if TYPE_CHECKING:
    # Avoid circular import for type declarations
    from .workspace import Workspace  # pragma: no cover


class Info(object):
    def __init__(self, workspace: Workspace):
        self.workspace = workspace

    def collect(self) -> Mapping[str, str]:
        """Return all known facts about the workspace"""
        return {
            # cut off "fact_"
            attr[5:]: getattr(self, attr)()
            for attr in self.__dir__()
            if attr.startswith("fact_")
        }

    def get_fact(self, fact_name: str) -> str:
        """Provide the single requested fact about the workspace"""
        attr = f"fact_{fact_name}"
        return getattr(self, attr)()  # type: ignore

    def fact_workspace_path(self) -> Optional[str]:
        return str(self.workspace.path)

    def fact_active_package(self) -> Optional[str]:
        package = self.workspace.active_package()
        return str(package.label_path) if package else None

    def fact_active_package_path(self) -> Optional[str]:
        package = self.workspace.active_package()
        return str(package.path) if package else None

    def fact_packages(self) -> List[str]:
        return [str(pkg.label_path) for pkg in self.workspace.packages()]

    def fact_py_project_poetry_name(self) -> Optional[str]:
        package = self.workspace.active_package()
        if not package or not package.path_exists("pyproject.toml"):
            return None

        toml = package.read_toml("pyproject.toml")
        return str(toml["tool"]["poetry"]["name"])
