from unittest import TestCase
from unittest.mock import patch

from mazel.fs import cd
from mazel.workspace import Workspace

from .utils import abspath


class InfoTest(TestCase):
    def run(self, result=None):
        with cd(abspath("examples/simple_workspace/package_b")):
            super().run(result=result)

    def setUp(self):
        workspace = Workspace.find()
        self.info = workspace.info()

    def tearDown(self):
        del self.info

    def test_get_fact(self):
        self.assertEqual(
            self.info.get_fact("workspace_path"),
            str(abspath("examples/simple_workspace")),
        )

    def test_get_fact_not_found(self):
        with self.assertRaises(AttributeError):
            self.info.get_fact("bad")

    def test_collect(self):
        facts = self.info.collect()
        self.assertCountEqual(
            facts.keys(),
            [
                "workspace_path",
                "active_package",
                "active_package_path",
                "packages",
                "py_project_poetry_name",
            ],
        )

    def test_fact_py_project_poetry_name(self):
        with patch("mazel.package.Package.path_exists", autospec=True) as path_exists:
            with patch("mazel.package.Package.read_toml", autospec=True) as read_toml:
                path_exists.return_value = True
                read_toml.return_value = {"tool": {"poetry": {"name": "foo.bar"}}}

                self.assertEqual(
                    self.info.get_fact("py_project_poetry_name"), "foo.bar"
                )

    def test_fact_py_project_poetry_name_no_pyproject_toml(self):
        with patch("mazel.package.Package.path_exists", autospec=True) as path_exists:
            path_exists.return_value = False
            self.assertIsNone(self.info.get_fact("py_project_poetry_name"))
