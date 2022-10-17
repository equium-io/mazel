from typing import Optional

import click

from mazel.label import Target
from mazel.package import Package

# Import module for easier patching during test
from . import label_common


class EchoHandler(label_common.TargetHandler):
    def handle(self, package: Package, target: Target) -> None:
        # Compute the label for display (may differ from the LabelRunner's label_value,
        # since a default can exist).
        label = f"{package.label_path}:{target}"
        click.secho(f"\u21D8 {label}", fg="cyan")


@label_common.label_command
def echo(
    label: str,
    with_ancestors: bool,
    with_descendants: bool,
    modified_since: Optional[str] = None,
) -> None:
    """For debugging what packages would get run by run/test, echo the package:target"""
    handler_cls = EchoHandler

    label_common.LabelRunner(
        handler=handler_cls(),
        default_target=Target("echo"),
        run_order=label_common.RunOrder.ORDERED,
        with_ancestors=with_ancestors,
        with_descendants=with_descendants,
        modified_since=modified_since,
    ).run(label)
