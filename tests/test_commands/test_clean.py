from click.testing import CliRunner

from mazel.commands.label_common import RunOrder
from mazel.label import Target
from mazel.main import cli

from .utils import LabelCommandTestCase


class CleanCommandTest(LabelCommandTestCase):
    def test_command(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["clean", "//package_b"])

        self.assertLabelRun(
            "//package_b",
            Target("clean"),
            run_order=RunOrder.REVERSED,
            with_ancestors=False,
            with_descendants=False,
        )

        self.assertEqual(result.exit_code, 0)
