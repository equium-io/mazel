from typing import TYPE_CHECKING, Iterable

from .base import Runtime

if TYPE_CHECKING:
    # Avoid circular import for type declarations
    from mazel.package import Package  # noqa  # pragma: no cover


class GoRuntime(Runtime):
    runtime_label = "go"

    def workspace_dependencies(self) -> Iterable["Package"]:
        # TODO Add support
        return iter([])
