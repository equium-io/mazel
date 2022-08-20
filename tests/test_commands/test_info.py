from unittest import TestCase

from click.testing import CliRunner

from mazel.fs import cd
from mazel.main import cli

from ..utils import abspath


class InfoCommandTest(TestCase):
    def run(self, result=None):
        # Ensure we are executing inside the workspace
        self.path = abspath("examples/simple_workspace/package_b")
        with cd(self.path):
            super().run(result=result)

    def test_command(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["info"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn(f"active_package_path: {self.path}", result.output)

    def test_single_fact(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["info", "active_package_path"])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, f"{self.path}\n")

    def test_bad_fact_name(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["info", "not_real"])

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, "Error: not_real not a valid FACT\n")

    # def test_cwd(self):
    #     # Use --cwd to make a different package active than our actual run directory
    #     path = abspath("examples/simple_workspace/nested/package_c")
    #     runner = CliRunner()
    #     result = runner.invoke(
    #         cli, ["info", "active_package_path", "--cwd", str(path)]
    #     )

    #     self.assertEqual(result.exit_code, 0)
    #     self.assertEqual(result.output, f"{self.path}\n")
