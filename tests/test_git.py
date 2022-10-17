from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, mock

from mazel.git import git_modified_files
from mazel.types import CommitRange


class GitModifiedFilesTest(TestCase):
    def run(self, result=None):
        with mock.patch(
            "mazel.git.subprocess.run", autospec=True
        ) as self.mock_run, mock.patch(
            "mazel.git.cd", autospec=True
        ) as self.mock_cd, TemporaryDirectory() as temp_dir:

            self.mock_run.return_value.stdout = (
                "package_a/file.py\npackage_b/other.py\n"
            )
            self.temp_dir = Path(temp_dir)
            super().run(result=result)

    def test(self):
        modified = git_modified_files(
            self.temp_dir, CommitRange.parse("7504f56..ba920f9")
        )

        self.assertEqual(
            modified, [Path("package_a/file.py"), Path("package_b/other.py")]
        )

        self.mock_run.assert_called_once_with(
            ["git", "diff", "--name-only", "7504f56", "ba920f9"],
            capture_output=True,
            text=True,
            check=True,
        )

        # Ensure git executed in expected directory
        self.mock_cd.assert_called_once_with(self.temp_dir)

    def test_default_to_head(self):
        git_modified_files(self.temp_dir, CommitRange.parse("7504f56"))

        self.mock_run.assert_called_once_with(
            ["git", "diff", "--name-only", "7504f56", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
