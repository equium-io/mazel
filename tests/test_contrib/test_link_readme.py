from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from click.testing import CliRunner

from mazel.fs import cd
from mazel.main import cli

from ..utils import example_workspace


class LinkReadmeTest(TestCase):
    def run(self, result=None):
        with patch(
            "mazel.contrib.link_readme.current_workspace", autospec=True
        ) as self.mock_current_workspace:
            workspace = example_workspace()
            self.mock_current_workspace.return_value = workspace

            with patch(
                "mazel.contrib.link_readme.get_root", autospec=True
            ) as self.mock_get_root:
                with TemporaryDirectory(dir=workspace.path) as temp_dir:
                    self.mock_get_root.return_value = Path(temp_dir)

                    with cd(workspace.path):
                        super().run(result=result)

    def test(self):
        # Doesn't really test anything, only that we don't get an exception
        runner = CliRunner()
        result = runner.invoke(cli, ["contrib", "link-readme"])

        self.assertEqual(result.exit_code, 0)
