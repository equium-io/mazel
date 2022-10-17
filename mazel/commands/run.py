from typing import Optional

# Import module for easier patching during test
from . import label_common


@label_common.label_command
def run(
    label: str,
    with_ancestors: bool,
    with_descendants: bool,
    modified_since: Optional[str] = None,
) -> None:
    """Runs a specific Makefile target.

    The equivalent of `cd mypackage; make shell`:

       mazel run //mypackage:shell
    """
    # Allow Ctrl-C to be passed to things like Jupyter Notebook
    handler_cls = label_common.MakeLabelPassInterrupt

    label_common.LabelRunner(
        handler=handler_cls(),
        default_target=None,
        run_order=label_common.RunOrder.ORDERED,
        with_ancestors=with_ancestors,
        with_descendants=with_descendants,
        modified_since=modified_since,
    ).run(label)
