from click.testing import CliRunner

from mazel.commands.label_common import RunOrder
from mazel.label import Target
from mazel.main import cli

from .utils import LabelCommandTestCase


class EchoCommandTest(LabelCommandTestCase):
    def test_command(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["echo", "//package_b"])

        self.assertLabelRun(
            "//package_b",
            Target("echo"),
            run_order=RunOrder.ORDERED,
            with_ancestors=False,
            with_descendants=False,
        )

        self.assertEqual(result.exit_code, 0)
