from __future__ import annotations

from functools import partial
from pathlib import Path
from typing import Callable, List, Optional, Union, overload

from .base import PathableConcept
from .exceptions import PackageNotFound
from .git import git_modified_files
from .graph import PackageGraph
from .info import Info
from .label import Label, ResolvedLabel, Target
from .package import Package
from .types import CommitRange


def package_scan(workspace: Workspace, path: Path) -> List[Package]:
    """
    Breadth-First Search to find all BUILD.toml files, stopping in each
    sub path once the BUILD.toml is found.  BFS instead of DFS, because we
    are likely to have multiple subdirectories below each BUILD.toml and
    os.scandir doesn't guarantee scan order.

    Unlike bazel, we do not presently support nested BUILD files. For us,
    the BUILD represents the top-level

    Alternative implementations:
    - Use `glob( "**/BUILD.toml", recursive=True)` -- would descend past
      the BUILD.toml
    - Use `os.walk()`, depth-first approach that would likely go deeper
      than needed
    - Use os.scandir() instead of Path.iterdir() (original implementation)
    """
    queued_dirs = []
    for entry in path.iterdir():
        if entry.is_file() and entry.name == Package.BUILD_TOML:
            # Found the BUILD.toml, we can stop descending.
            return [Package(entry.parent, workspace=workspace)]

        # TODO Handle nested Workspaces. Do not scan the nested Workspace.
        #   Would need to delay the prior BUILD.toml return, since it would
        #   belong to this nested WORKSPACE.  Below is an insufficient
        #   implementations
        # elif entry.is_file() and entry.name == WORKSPACE_TOML:
        #    # Found a nested workspace, so stop
        #    return []

        elif (
            entry.is_dir()
            # Ignore hidden directories (i.e. .git .venv)
            and not entry.name.startswith(".")
        ):
            queued_dirs.append(entry)

    results = []
    for queued_dir in queued_dirs:
        # recursive scan
        results.extend(package_scan(workspace, queued_dir))
    return results


@overload
def locate_upwards(
    locate: str, fn: Callable[[Path], Package], stopdir: Path = None, cwd: Path = None
) -> Optional[Package]:
    ...


@overload
def locate_upwards(
    locate: str, fn: Callable[[Path], Workspace], stopdir: Path = None, cwd: Path = None
) -> Optional[Workspace]:
    ...


def locate_upwards(
    locate: str,
    fn: Callable[[Path], Union[Package, Workspace]],
    stopdir: Path = None,
    cwd: Path = None,
) -> Union[None, Package, Workspace]:
    """
    Walk up the directory tree, trying to find the `locate` file's directory.

    When found will call `fn(directory)`.

    Can limit how far up the directory tree we go by `stopdir`, but will
    naturally stop when the filesystem root is reached.
    """
    curdir = Path.cwd() if cwd is None else cwd
    root = Path(curdir.root)

    while True:
        path = curdir.joinpath(locate)
        if path.exists():
            return fn(curdir)
        elif curdir == root or curdir == stopdir:
            # We've reached the root of the filesystem, so stop
            return None
        else:
            curdir = curdir.parent


class Workspace(PathableConcept):
    WORKSPACE_TOML = "WORKSPACE.toml"

    @classmethod
    def find(cls, cwd: Path = None) -> Optional[Workspace]:
        """
        Walk up the directory tree, trying to find the WORKSPACE file,
        which indicates the workspace path
        """
        return locate_upwards(locate=cls.WORKSPACE_TOML, fn=cls, cwd=cwd)

    def active_package(self, cwd: Path = None) -> Optional[Package]:
        """Current working directory's Package"""
        return locate_upwards(
            locate=Package.BUILD_TOML,
            fn=partial(Package, workspace=self),
            stopdir=self.path,
            cwd=cwd,
        )

    def info(self) -> Info:
        return Info(self)

    def packages(self) -> List[Package]:
        """Scans for all Packages inside the Workspace"""
        if not hasattr(self, "_packages"):
            self._packages = package_scan(self, self.path)
        return self._packages

    def graph(self) -> PackageGraph:
        return PackageGraph.from_packages(self.packages())

    def _abspath(self, package_path: Optional[str]) -> Optional[Path]:
        if package_path is None:
            return None
        elif Label.is_absolute(package_path):
            path = package_path.lstrip("/")  # Remove leading //
            return self.path.joinpath(path)
        else:
            # Relative path
            return Path.cwd().joinpath(package_path)

    def get_package(self, path: Optional[Path]) -> Package:
        if path is not None:
            for package in self.packages():
                if package.path == path:
                    return package
        raise PackageNotFound(f"No package found for {path}")

    def resolve_label_path(self, package_path: str) -> Package:
        """Resolve a package_path to a Package"""
        # TODO pass in active_package and resolve relative paths
        return self.get_package(self._abspath(package_path))

    def resolve_label(self, label: Label, cwd: Path = None) -> ResolvedLabel:
        """Resolves the Label to one or more Packages, with a Target"""
        active = self.active_package(cwd=cwd)
        matched_packages: List[Package] = []

        requested_path = self._abspath(label.package_path)
        if requested_path is None:
            if active is None:
                raise PackageNotFound(
                    "Not currently in a package and no package label specified"
                )
            matched_packages.append(active)
        else:
            for package in self.packages():
                if (
                    package.path == requested_path
                    or requested_path in package.path.parents
                ):
                    matched_packages.append(package)

            if not matched_packages:
                raise PackageNotFound(f"No package found for {label}")

        target = Target(label.target_name) if label.target_name else None

        return ResolvedLabel(matched_packages, target)

    def modified_files(self, commit_range: CommitRange) -> list[Path]:
        """
        What files were modified between git commits.

        Typically prefer Workspace.modified_packages()

        `commit_to` defaults to HEAD.
        """
        modified = git_modified_files(repo_dir=self.path, commit_range=commit_range)
        return [self.path / path for path in modified]

    def modified_packages(self, commit_range: CommitRange) -> list[Package]:
        """
        What packages have modified files between git commits.

        `commit_to` defaults to HEAD.
        """
        modified_files = self.modified_files(commit_range=commit_range)

        # All the paths from `git diff --name-only` should be files, so get the unique
        # set of directories to compare against the packages' directories
        modified_dirs = sorted(list(set([path.parent for path in modified_files])))

        # Naive O(N^2) algorithm, lot's of options to improve
        modified_packages = []
        for path in modified_dirs:
            # Include this path, since we've already done .parent to uniquify the list
            parents = list(path.parents) + [path]
            for package in self.packages():
                if package.path in parents and package not in modified_packages:
                    modified_packages.append(package)

        return modified_packages
