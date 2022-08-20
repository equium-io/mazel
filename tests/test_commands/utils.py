from unittest import TestCase
from unittest.mock import ANY, patch

from mazel.fs import cd

from ..utils import abspath


class CommandTestCase(TestCase):
    def run(self, result=None):
        # Ensure we are executing inside the workspace
        with cd(abspath("examples/simple_workspace")):
            super().run(result=result)


class LabelCommandTestCase(CommandTestCase):
    def run(self, result=None):
        with patch(
            "mazel.commands.label_common.LabelRunner", autospec=True
        ) as self.mock_runner:
            super().run(result=result)

    def assertLabelRun(self, expected_label, expected_default_target, **kwargs):
        self.mock_runner.assert_called_once_with(
            default_target=expected_default_target,
            handler=ANY,  # WARNING: non-specific, consider making more specific
            **kwargs
        )
        self.mock_runner.return_value.run.assert_called_once_with(expected_label)
