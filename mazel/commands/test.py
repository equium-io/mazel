from typing import Optional

import click

from mazel.label import Target

# Import module for easier patching during test
from . import label_common


@label_common.label_command
@click.option(
    # Replicated from bazel:
    #   https://docs.bazel.build/versions/master/user-manual.html#flag--test_output
    "--test_output",
    type=click.Choice(["streamed", "errors"]),
    default="streamed",
    help="Only show stdout/stderr after error, or stream everything.",
)
def test(
    label: str,
    test_output: str,
    with_ancestors: bool,
    with_descendants: bool,
    modified_since: Optional[str] = None,
) -> None:
    handler_cls = (
        label_common.MakeLabelCaptureErrors
        if test_output == "errors"
        else label_common.MakeLabel
    )

    label_common.LabelRunner(
        handler=handler_cls(),
        default_target=Target("test"),
        run_order=label_common.RunOrder.ORDERED,
        with_ancestors=with_ancestors,
        with_descendants=with_descendants,
        modified_since=modified_since,
    ).run(label)
