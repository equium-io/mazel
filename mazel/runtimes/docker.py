from typing import TYPE_CHECKING, Iterable

from .base import Runtime

if TYPE_CHECKING:
    # Avoid circular import for type declarations
    from mazel.package import Package  # noqa  # pragma: no cover


class DockerRuntime(Runtime):
    runtime_label = "docker"

    def workspace_dependencies(self) -> Iterable["Package"]:
        # TODO Support relative dependencies parsed from the Dockerfile, for now we
        # require they are all specified in BUILD.toml's depends_on
        return iter([])
