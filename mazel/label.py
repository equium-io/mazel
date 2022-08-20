from __future__ import annotations

from typing import List, Optional

from .package import Package


class Label(object):
    """
    Representation of a package and/or target, following bazel's Labels [1].

    Not a full or even accurate re-implementation of bazel's Labels.

    Examples::
        //
        //apps/pkg:target
        //apps/pkg
        //apps             # May not be valid bazel
        pkg:target
        :target
        target


    [1]: https://docs.bazel.build/versions/2.0.0/build-ref.html#labels
    """

    def __init__(self, package_path: Optional[str], target_name: Optional[str]):
        # TODO Enforce package_path and target_name  validity?
        self.package_path = package_path
        self.target_name = target_name

    @classmethod
    def parse(cls, value: str) -> Label:
        if value is None:
            return cls(None, None)

        components = value.split(":")
        if len(components) == 1:
            item = components[0]
            if cls.is_absolute(item):
                package_path, target_name = item, None
            else:
                # Lacking a path specifier, assume the single component
                # refers to the target_name
                package_path, target_name = None, item  # type: ignore
        else:
            # TODO Consider handling error of > 2 parts
            package_path, target_name = components[0:2]

        # Turn empty strings from .split() into None
        package_path = package_path or None  # type: ignore
        target_name = target_name or None

        return cls(package_path, target_name)

    @staticmethod
    def is_absolute(package_path: Optional[str]) -> bool:
        return package_path is not None and package_path.startswith("//")

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Label)
            and self.package_path == other.package_path
            and self.target_name == other.target_name
        )

    def __str__(self) -> str:
        package_path = self.package_path or ""
        target_name = self.target_name or ""
        return f"{package_path}:{target_name}"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self}>"


class ResolvedLabel(object):
    def __init__(self, packages: List[Package], target: Optional[Target]):
        self.packages = packages
        self.target = target

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, ResolvedLabel)
            and self.packages == other.packages
            and self.target == other.target
        )

    def __str__(self) -> str:
        return f"{self.packages}:{self.target}"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self}>"


class Target(object):
    def __init__(self, name: str):
        # TODO Validate target names
        self.name = name

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Target) and self.name == other.name

    def __str__(self) -> str:
        return f"{self.name}"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self}>"
