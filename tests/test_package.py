from pathlib import Path
from unittest import TestCase
from unittest.mock import Mock, PropertyMock, patch

from mazel.exceptions import InvalidBuildToml, PackageNotFound
from mazel.package import Package
from mazel.runtimes import PythonRuntime
from mazel.workspace import Workspace

from .utils import abspath, example_workspace


def make_package(path: str, workspace=None) -> Package:
    if workspace is None:
        workspace = example_workspace()
    return Package(abspath(path), workspace=workspace)


class PackageTest(TestCase):
    def test_eq(self):
        # same path, different instance
        one = make_package("examples/simple_workspace/package_a")
        two = make_package("examples/simple_workspace/package_a")

        three = make_package("examples/simple_workspace/package_b")

        self.assertIsNot(one, two)

        self.assertTrue(one == two)
        self.assertFalse(one != two)

        self.assertFalse(one == three)
        self.assertTrue(one != three)

        self.assertFalse(one == None)  # noqa
        self.assertTrue(one != None)  # noqa

    def test_hash(self):
        one = make_package("examples/simple_workspace/package_a")
        two = make_package("examples/simple_workspace/package_b")

        self.assertNotEqual(hash(one), hash(two))

    def test_str(self):
        package = make_package("examples/simple_workspace/package_a")
        self.assertEqual(str(package), "package_a")

    def test_repr(self):
        package = make_package("examples/simple_workspace/package_a")
        self.assertEqual(repr(package), "<Package: package_a>")

    def test_label_path(self):
        package = Package(
            abspath("examples/simple_workspace/package_a"),
            workspace=Workspace(abspath("examples/simple_workspace")),
        )

        self.assertEqual(package.label_path, "//package_a")

    def test_label_path_nested(self):
        package = Package(
            abspath("examples/simple_workspace/nested/package_c"),
            workspace=Workspace(abspath("examples/simple_workspace")),
        )

        self.assertEqual(package.label_path, "//nested/package_c")

    def test_read_toml(self):
        package = Package(
            abspath("examples/simple_workspace/package_b"),
            workspace=Workspace(abspath("examples/simple_workspace")),
        )
        expected = {"package": {"runtimes": ["python"]}}
        self.assertEqual(package.read_toml("BUILD.toml"), expected)

    def test_build_toml(self):
        # similar test to test_read_toml
        package = Package(
            abspath("examples/simple_workspace/package_a"),
            workspace=Workspace(abspath("examples/simple_workspace")),
        )
        expected = {
            "package": {
                "runtimes": ["python", "docker"],
                "depends_on": ["//package_b"],
            }
        }
        self.assertEqual(package.build_toml, expected)

    def test_read_path(self):
        package = Package(
            abspath("examples/simple_workspace/package_b"),
            workspace=Workspace(abspath("examples/simple_workspace")),
        )
        expected = """[package]\nruntimes = ["python"]\n"""
        self.assertEqual(package.read_path("BUILD.toml"), expected)

    def test_path_exists(self):
        package = Package(
            abspath("examples/simple_workspace/package_a"),
            workspace=Workspace(abspath("examples/simple_workspace")),
        )
        self.assertTrue(package.path_exists("BUILD.toml"))
        self.assertFalse(package.path_exists("does_not_exist"))

    def test_relative_package(self):
        workspace = Workspace(abspath("examples/simple_workspace"))
        package = Package(
            abspath("examples/simple_workspace/package_a"),
            workspace=workspace,
        )

        sibling = package.relative_package(Path("../nested/package_c"))
        self.assertEqual(sibling.workspace, workspace)
        self.assertEqual(
            sibling.path, abspath("examples/simple_workspace/nested/package_c")
        )

    def test_relative_package_not_found(self):
        workspace = Workspace(abspath("examples/simple_workspace"))
        package = Package(
            abspath("examples/simple_workspace/package_a"),
            workspace=workspace,
        )

        with self.assertRaises(PackageNotFound):
            package.relative_package(Path("../package_x"))

    def test_runtimes(self):
        package = Package(
            abspath("examples/simple_workspace/package_a"),
            workspace=Workspace(abspath("examples/simple_workspace")),
        )
        package.read_toml = Mock(return_value={"package": {"runtimes": ["python"]}})

        runtimes = package.runtimes()
        self.assertEqual(len(runtimes), 1)
        self.assertIsInstance(runtimes[0], PythonRuntime)

    def test_runtimes_not_array(self):
        package = Package(
            abspath("examples/simple_workspace/package_a"),
            workspace=Workspace(abspath("examples/simple_workspace")),
        )
        package.read_toml = Mock(return_value={"package": {"runtimes": "python"}})

        runtimes = package.runtimes()
        self.assertEqual(len(runtimes), 1)
        self.assertIsInstance(runtimes[0], PythonRuntime)

    def test_runtimes_no_runtime_defined(self):
        package = Package(
            abspath("examples/simple_workspace/package_a"),
            workspace=Workspace(abspath("examples/simple_workspace")),
        )
        package.read_toml = Mock(return_value={"package": {}})

        runtimes = package.runtimes()
        self.assertEqual(len(runtimes), 0)

    def test_runtimes_no_package_section(self):
        package = Package(
            abspath("examples/simple_workspace/package_a"),
            workspace=Workspace(abspath("examples/simple_workspace")),
        )
        package.read_toml = Mock(return_value={})

        with self.assertRaises(InvalidBuildToml):
            package.runtimes()

    def test_depends_on(self):
        package = Package(
            abspath("examples/simple_workspace/package_a"),
            workspace=Workspace(abspath("examples/simple_workspace")),
        )

        self.assertCountEqual(
            package.depends_on(),
            [
                package.relative_package("../package_b"),
                package.relative_package("../nested/package_c"),
            ],
        )

    def test_depends_on_duplicate(self):
        package = Package(
            abspath("examples/simple_workspace/package_b"),
            workspace=Workspace(abspath("examples/simple_workspace")),
        )

        with patch(
            "mazel.runtimes.python.PythonRuntime.pyproject_toml",
            new_callable=PropertyMock,
        ) as mock_pyproject:
            mock_pyproject.return_value = {
                "tool": {
                    "poetry": {
                        "dependencies": {"package_c": {"path": "../nested/package_c"}}
                    }
                }
            }

            self.assertCountEqual(
                package.depends_on(), [package.relative_package("../nested/package_c")]
            )
