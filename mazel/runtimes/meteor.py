from typing import TYPE_CHECKING, Iterable

from .base import Runtime
from .javascript import JavascriptRuntime

if TYPE_CHECKING:
    # Avoid circular import for type declarations
    from mazel.package import Package  # noqa  # pragma: no cover


class MeteorRuntime(Runtime):
    """Enhances the Javascript runtime to support Meteor applications.

    Scans for relative local packages in packages/

    https://guide.meteor.com/writing-atmosphere-packages.html#local-packages
    """

    runtime_label = "meteor"

    def __init__(self, package: "Package"):
        super().__init__(package)

        # Avoid packages that use the meteor runtime from also needing to declare
        # it uses the javascript runtime
        self.javascript_runtime = JavascriptRuntime(package)

    def workspace_dependencies(self) -> Iterable["Package"]:
        deps = list(self.javascript_runtime.workspace_dependencies()) + list(
            self.dependencies()
        )
        return deps

    def dependencies(self) -> Iterable["Package"]:
        # The packages/ folder is the way to include local Meteor packages (not to be
        # confused with mazel packages)
        pkgs_dir = self.package.path.joinpath("packages")
        if not pkgs_dir.exists():
            return []

        for path in pkgs_dir.iterdir():
            if path.is_symlink():
                yield self.package.relative_package(path)
