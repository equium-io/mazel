from __future__ import annotations

import abc
import signal
import subprocess
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Callable, List, Optional

import click

from mazel.graph import Node, PackageGraph
from mazel.label import Label, Target
from mazel.package import Package
from mazel.types import CommitRange
from mazel.workspace import Workspace

from .utils import current_workspace

RunOrder = Enum("RunOrder", "UNORDERED ORDERED REVERSED")


def label_command(fn: Callable[..., None]) -> click.Command:
    """Reusable decorator for label-based click commands"""
    fn = click.command()(fn)
    fn = click.argument("label", required=False)(fn)
    fn = click.option("--with-ancestors", is_flag=True, default=False)(fn)
    fn = click.option("--with-descendants", is_flag=True, default=False)(fn)
    fn = click.option(
        "--modified-since",
        default=None,
        help=(
            "Only run for packages with modified files according to git. Takes in a "
            "commit like object, e.g. 39fc076 or a range 39fc076..6ff72ca. End commit "
            "defaults to HEAD"
        ),
    )(fn)
    return fn


# TODO Consider generalizing package_order beyond label_common
# WARN Walk the entire graph multiple times, consider optimizing
def package_order(
    packages: List[Package],
    workspace: Workspace,
    run_order: RunOrder = RunOrder.UNORDERED,
    with_ancestors: bool = False,
    with_descendants: bool = False,
) -> List[Package]:

    graph = workspace.graph()
    if run_order == run_order.REVERSED:
        graph = graph.invert()

    # Ensure the order the subset in `packages` aligns with the order of the superset
    # in `expected`, which defines the directed-graph order
    expected = list(graph.consume_tree())

    packages = expand_ancestry(packages, graph, with_ancestors, with_descendants)

    if run_order == RunOrder.UNORDERED:
        return packages

    return sorted(packages, key=lambda pkg: expected.index(pkg))


def expand_ancestry(
    initial: List[Package],
    graph: PackageGraph,
    with_ancestors: bool = False,
    with_descendants: bool = False,
) -> List[Package]:
    packages: List[Package] = []

    def recurse(node: Node) -> None:
        # This node has already been processed, don't need to readd it or
        # its parents/chilren
        if node.package in packages:
            return

        packages.append(node.package)

        if with_ancestors:
            # Add parents and recursive to grandparents until exhausted
            for parent in node.parents:
                recurse(parent)

        if with_descendants:
            # Add children and recursive to grandchildren until exhausted
            for child in node.children:
                recurse(child)

    # Find the nodes associated with the input packages (since nodes have
    # parents/children), then add the package and if requested,
    # the ancestors and/or descendants
    for node in graph.nodes():
        if node.package in initial:
            recurse(node)

    return packages


class LabelRunner:
    def __init__(
        self,
        handler: TargetHandler,
        default_target: Optional[Target],
        run_order: RunOrder = RunOrder.UNORDERED,
        with_ancestors: bool = False,
        with_descendants: bool = False,
        modified_since: Optional[str] = None,
    ):
        self.handler = handler
        self.default_target = default_target
        self.run_order = run_order
        self.with_ancestors = with_ancestors
        self.with_descendants = with_descendants

        self.modified_range = (
            CommitRange.parse(modified_since) if modified_since else None
        )

        self.workspace = current_workspace()

    def run(self, label_value: str) -> None:
        label = Label.parse(label_value)
        resolved = self.workspace.resolve_label(label)
        target = resolved.target if resolved.target else self.default_target

        assert target is not None, "Must have a label target or a default target"

        self.process_packages(resolved.packages, target)

    def process_packages(self, packages: List[Package], target: Target) -> None:
        errors = []

        if self.modified_range is not None:
            modified_packages = self.workspace.modified_packages(
                commit_range=self.modified_range
            )
            packages = [pkg for pkg in packages if pkg in modified_packages]

        for pkg in package_order(
            packages=packages,
            workspace=self.workspace,
            run_order=self.run_order,
            with_ancestors=self.with_ancestors,
            with_descendants=self.with_descendants,
        ):
            # Try to run for packages, storing the errors for later. Could
            # consider --fail-fast in the future
            try:
                self.handler.handle(pkg, target)
            except click.ClickException as e:
                errors.append(e)

        if errors:
            # Show the first error
            raise errors[0]


class TargetHandler(abc.ABC):
    @abc.abstractmethod
    def handle(self, package: Package, target: Target) -> None:
        pass


class MakeLabel(TargetHandler):
    def handle(self, package: Package, target: Target) -> None:
        if not self.target_exists(package, target):
            return

        # Compute the label for display (may differ from the LabelRunner's label_value,
        # since a default can exist).
        label = f"{package.label_path}:{target}"

        # Indicate what package is being executed.
        click.secho(f"\u21D8 {label}", fg="cyan")

        start = datetime.now()
        try:
            self.process(["make", "-s", str(target)], package.path)

            # check mark in green
            click.secho(
                f"\u2714 {label} (Elapsed time: {datetime.now() - start})",
                fg="green",
            )
        except subprocess.CalledProcessError as e:
            # X mark in red
            click.secho(
                f"\u2718 {label} (Elapsed time: {datetime.now() - start})",
                fg="red",
                bold=True,
            )
            raise click.ClickException(" ".join(e.cmd))

    def target_exists(self, package: Package, target: Target) -> bool:
        """
        Do a dry-run execution of make to see if the target exists in the Makefile.

        - https://www.gnu.org/software/make/manual/html_node/Instead-of-Execution.html
        - https://www.gnu.org/software/make/manual/html_node/Running.html
        """
        # TODO Consider if we want some warning / notice. As-is is good for `mazel test`
        #   but probably not designed for `mazel run`
        dryrun = subprocess.run(
            ["make", "-n", str(target)],
            cwd=package.path,
            capture_output=True,
            encoding="utf-8",
        )
        return not (
            dryrun.returncode == 2 and "No rule to make target" in dryrun.stderr
        )

    def process(self, cmd: List[str], cwd: Path) -> None:
        subprocess.run(cmd, cwd=cwd, check=True)


class MakeLabelCaptureErrors(MakeLabel):
    """
    Capture the stdout/stderr of the process, only display if the process did
    not exit normally
    """

    def process(self, cmd: List[str], cwd: Path) -> None:
        try:
            subprocess.run(
                cmd,
                cwd=cwd,
                check=True,
                text=True,
                # WARNING: PIPE buffered in memory, if extremely large, could
                #  cause issues
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
        except subprocess.CalledProcessError as e:
            # Only push output (stderr redirected to stderr), if there was a problem
            click.secho(e.stdout)
            raise e


class MakeLabelPassInterrupt(MakeLabel):
    """
    When a SIGINT (KeyboardInterrupt) occurs, pass it to the sub process, allowing
    it to decide to exit / cleanup.

    Jupyter Notebook prompts the user to confirm exit, which when running with
    `subprocess.run` never occured, and led to zombie processes running.
    """

    def process(self, cmd: List[str], cwd: Path) -> None:
        # subprocess.run doesn't expose the underlying process for us to hook into,
        # so we need to use the lower-level Popen.  We have to re-implement a subset
        # of it's behavior.

        with subprocess.Popen(cmd, cwd=cwd) as process:
            done = False
            called_sigint = False
            while not done:
                try:

                    # WARNING: we push stderr to stdout, this may not be desirable
                    # for line in process.stdout:
                    #    sys.stdout.write(line)

                    retcode, done = process.wait(), True

                    if called_sigint and retcode == -(signal.SIGINT):
                        # If KeyboardInterrupt was called, subprocess will set the
                        # returncode to `-signal`.
                        # WARN: There is a potential loss of information if the
                        # subprocess later suffers an actual error.
                        pass
                    elif retcode:
                        raise subprocess.CalledProcessError(retcode, process.args)
                except KeyboardInterrupt:
                    # Jupyter notebooks prompt the user to cancel, so we want to pass
                    # the SIGINT down the underlying process. If the user cancels the
                    # shutdown, we re-enter the while loop
                    called_sigint = True
                    process.send_signal(signal.SIGINT)
