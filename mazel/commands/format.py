from typing import Optional

from mazel.label import Target

# Import module for easier patching during test
from . import label_common


# TODO should this be a top-level command? It is the equivalent of
#   `mazel run :format`
# TODO should we allow a label-based target instead of always using "format"?
@label_common.label_command
def format(
    label: str,
    with_ancestors: bool,
    with_descendants: bool,
    modified_since: Optional[str] = None,
) -> None:
    label_common.LabelRunner(
        handler=label_common.MakeLabel(),
        default_target=Target("format"),
        with_ancestors=with_ancestors,
        with_descendants=with_descendants,
        modified_since=modified_since,
    ).run(label)
