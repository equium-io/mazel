from unittest import TestCase
from unittest.mock import patch

from click.testing import CliRunner

from mazel.main import cli

from ..utils import example_workspace

EXPECTED_YAML = """\
# Do not edit manually, regenerate with `mazel contrib dependabot`
version: 2
updates:
- package-ecosystem: pip
  directory: /package_a
  open-pull-requests-limit: 10
  schedule:
    interval: monthly
  ignore:
  - dependency-name: '*'
    update-types:
    - version-update:semver-patch
- package-ecosystem: pip
  directory: /package_b
  open-pull-requests-limit: 10
  schedule:
    interval: monthly
  ignore:
  - dependency-name: '*'
    update-types:
    - version-update:semver-patch
"""


class DependabotTest(TestCase):
    def run(self, result=None):
        with patch(
            "mazel.contrib.dependabot.write_config_yml", autospec=True
        ) as self.mock_write:

            with patch(
                "mazel.contrib.dependabot.read_config_yml", autospec=True
            ) as self.mock_read:
                self.mock_read.return_value = ""

                with patch(
                    "mazel.contrib.dependabot.current_workspace", autospec=True
                ) as self.mock_current_workspace:
                    self.mock_current_workspace.return_value = example_workspace()

                    super().run(result=result)

    def test_write_differs(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["contrib", "dependabot"])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, ".github/dependabot.yml updated\n")

        path = example_workspace().path.joinpath(".github/dependabot.yml")
        self.mock_write.assert_called_once_with(path, EXPECTED_YAML)
        self.mock_read.assert_called_once_with(path)

    def test_write_same(self):
        self.mock_read.return_value = EXPECTED_YAML

        runner = CliRunner()
        result = runner.invoke(cli, ["contrib", "dependabot"])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, ".github/dependabot.yml is current\n")
        self.assertFalse(self.mock_write.called)

    def test_check_differs(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["contrib", "dependabot", "--check"])

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(
            result.output,
            (
                "Error: .github/dependabot.yml is out of date. "
                "Run `mazel contrib dependabot`\n"
            ),
        )
        self.assertFalse(self.mock_write.called)

    def test_check_same(self):
        self.mock_read.return_value = EXPECTED_YAML

        runner = CliRunner()
        result = runner.invoke(cli, ["contrib", "dependabot", "--check"])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, ".github/dependabot.yml is current\n")
        self.assertFalse(self.mock_write.called)
