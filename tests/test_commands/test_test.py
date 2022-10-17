import click
from click.testing import CliRunner

from mazel.commands.label_common import MakeLabel, MakeLabelCaptureErrors, RunOrder
from mazel.label import Target
from mazel.main import cli

from .utils import LabelCommandTestCase


class TestCommandTest(LabelCommandTestCase):
    def test_command(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["test", "//package_b"])

        self.assertLabelRun(
            "//package_b",
            Target("test"),
            run_order=RunOrder.ORDERED,
            with_ancestors=False,
            with_descendants=False,
            modified_since=None,
        )
        self.assertIsInstance(
            self.mock_runner.call_args_list[0][1]["handler"], MakeLabel
        )

        self.assertEqual(result.exit_code, 0)

    def test_error(self):
        self.mock_runner.return_value.run.side_effect = click.ClickException("message")

        runner = CliRunner()
        result = runner.invoke(cli, ["test", "//package_b"])

        self.assertLabelRun(
            "//package_b",
            Target("test"),
            run_order=RunOrder.ORDERED,
            with_ancestors=False,
            with_descendants=False,
            modified_since=None,
        )

        self.assertEqual(result.exit_code, 1)

    def test_test_output_errors(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["test", "//package_b", "--test_output=errors"])

        self.assertLabelRun(
            "//package_b",
            Target("test"),
            run_order=RunOrder.ORDERED,
            with_ancestors=False,
            with_descendants=False,
            modified_since=None,
        )
        self.assertIsInstance(
            self.mock_runner.call_args_list[0][1]["handler"], MakeLabelCaptureErrors
        )

        self.assertEqual(result.exit_code, 0)
