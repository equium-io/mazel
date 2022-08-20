import abc
from collections import Counter
from typing import TYPE_CHECKING, Iterable, List, Type

from mazel.exceptions import DuplicateDependency, RuntimeNotFound

if TYPE_CHECKING:
    # Avoid circular import for type declarations
    from mazel.package import Package  # pragma: no cover


class Runtime(metaclass=abc.ABCMeta):
    def __init__(self, package: "Package"):
        self.package = package

    @classmethod
    def implementations(cls) -> List[Type["Runtime"]]:
        # Use __subclasses__ as a cheap registry (requires the implementation to
        # be imported in mazel.runtimes.__init__)
        return cls.__subclasses__()

    @classmethod
    def resolve(cls, runtime_label: str, package: "Package") -> "Runtime":
        """Lookup the Runtime implementation by the runtime_label"""
        for runtime_cls in cls.implementations():
            if runtime_cls.runtime_label == runtime_label:
                return runtime_cls(package)

        raise RuntimeNotFound(f"No Runtime defined for label={runtime_label}")

    @abc.abstractmethod
    def workspace_dependencies(self) -> Iterable["Package"]:
        """
        Returns an iterable with Packages that this package implicitly depends upon
        via runtime-specific configuration such as pyproject.toml or package.json.
        """

    @property
    @abc.abstractmethod
    def runtime_label(self) -> str:
        """The unique str identifer for the Runtime implementation"""


def check_duplicates(values: List[str]) -> None:
    c = Counter(values)

    overlap = [v for v, count in c.items() if count > 1]
    if len(overlap) > 0:
        raise DuplicateDependency(f"Dependencies listed multiple times: {overlap}")
