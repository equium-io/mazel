from click.testing import CliRunner

from mazel.label import Target
from mazel.main import cli

from .utils import LabelCommandTestCase


class FormatCommandTest(LabelCommandTestCase):
    def test_command(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["format", "//package_b"])

        self.assertLabelRun(
            "//package_b",
            Target("format"),
            with_ancestors=False,
            with_descendants=False,
        )

        self.assertEqual(result.exit_code, 0)
