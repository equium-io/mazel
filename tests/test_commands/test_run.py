from click.testing import CliRunner

from mazel.commands.label_common import MakeLabelPassInterrupt, RunOrder
from mazel.main import cli

from .utils import LabelCommandTestCase


class RunCommandTest(LabelCommandTestCase):
    def test_command(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["run", "//package_b:action"])

        self.assertLabelRun(
            "//package_b:action",
            None,
            run_order=RunOrder.ORDERED,
            with_ancestors=False,
            with_descendants=False,
        )
        self.assertIsInstance(
            self.mock_runner.call_args_list[0][1]["handler"], MakeLabelPassInterrupt
        )

        self.assertEqual(result.exit_code, 0)
