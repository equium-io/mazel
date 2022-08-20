from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from mazel.exceptions import PackageNotFound
from mazel.fs import cd
from mazel.info import Info
from mazel.label import Label, ResolvedLabel, Target
from mazel.package import Package
from mazel.workspace import Workspace

from .utils import abspath, example_workspace


class WorkspaceDunderTest(TestCase):
    def test_eq(self):
        one = Workspace.find()
        two = Workspace.find()  # same path, different instance
        three = example_workspace()

        self.assertIsNot(one, two)

        self.assertTrue(one == two)
        self.assertFalse(one != two)

        self.assertFalse(one == three)
        self.assertTrue(one != three)

        self.assertFalse(one == None)  # noqa
        self.assertTrue(one != None)  # noqa

    def test_hash(self):
        self.assertIsNotNone(hash(Workspace.find()))

    def test_str(self):
        workspace = example_workspace()
        self.assertEqual(str(workspace), "simple_workspace")

    def test_repr(self):
        workspace = example_workspace()
        self.assertEqual(repr(workspace), "<Workspace: simple_workspace>")


class WorkspaceFindTest(TestCase):
    def test_using_getcwd(self):
        # WARN: Britle test, since it uses the layout of our repository.
        expected = Workspace(abspath(".."))
        self.assertEqual(Workspace.find(), expected)

    def test_from_workspace_root(self):
        expected = example_workspace()
        path = abspath("examples/simple_workspace")
        self.assertEqual(Workspace.find(path), expected)

    def test_from_package(self):
        expected = example_workspace()
        path = abspath("examples/simple_workspace/package_a")
        self.assertEqual(
            Workspace.find(path),
            expected,
        )

    def test_from_nested_dir(self):
        expected = example_workspace()
        path = abspath("examples/simple_workspace/package_a/nested")
        self.assertEqual(
            Workspace.find(path),
            expected,
        )

    def test_from_non_package(self):
        expected = example_workspace()
        path = abspath("examples/simple_workspace/non_package")
        self.assertEqual(
            Workspace.find(path),
            expected,
        )

    def test_no_workspace(self):
        with TemporaryDirectory() as tmpdir:
            self.assertIsNone(Workspace.find(Path(tmpdir)))


class WorkspaceInfoTest(TestCase):
    def setUp(self):
        self.workspace = example_workspace()

    def tearDown(self):
        del self.workspace

    def test_info(self):
        info = self.workspace.info()
        self.assertIsInstance(info, Info)
        self.assertEqual(info.workspace, self.workspace)


class WorkspacePackageTest(TestCase):
    def setUp(self):
        self.workspace = example_workspace()

    def tearDown(self):
        del self.workspace

    def test_packages(self):
        packages = self.workspace.packages()
        expected = [
            Package(abspath("examples/simple_workspace/package_a"), self.workspace),
            Package(abspath("examples/simple_workspace/package_b"), self.workspace),
            Package(
                abspath("examples/simple_workspace/nested/package_c"), self.workspace
            ),
        ]
        self.assertCountEqual(packages, expected)

    def assertActivePackage(self, path, expected):
        self.assertEqual(self.workspace.active_package(abspath(path)), expected)

    def test_active_package_in_package_root(self):
        expected = Package(
            abspath("examples/simple_workspace/package_a"), self.workspace
        )
        self.assertActivePackage("examples/simple_workspace/package_a", expected)

    def test_active_package_in_package_subdir(self):
        expected = Package(
            abspath("examples/simple_workspace/package_b"), self.workspace
        )
        self.assertActivePackage("examples/simple_workspace/package_b/nested", expected)

    def test_active_package_in_workspace_root(self):
        self.assertActivePackage("examples/simple_workspace", None)

    def test_active_package_in_non_package_(self):
        self.assertActivePackage("examples/simple_workspace/non_package", None)

    def test_graph(self):
        graph = self.workspace.graph()
        self.assertTrue(len(graph._nodes), 3)


class WorkspaceResolveLabelTest(TestCase):
    def setUp(self):
        self.workspace = example_workspace()

    def tearDown(self):
        del self.workspace

    def run(self, result=None):
        # Run these resolve tests from a specific location inside the workspace
        # to ensure that the cwd is used as the active_package when needed and
        # no other time.
        with cd(abspath("examples/simple_workspace/nested/package_c")):
            super().run(result=result)

    def test_full_path(self):
        expected = ResolvedLabel(
            [Package(abspath("examples/simple_workspace/package_b"), self.workspace)],
            Target("action"),
        )

        self.assertEqual(
            self.workspace.resolve_label(Label("//package_b", "action")), expected
        )

    def test_no_target(self):
        expected = ResolvedLabel(
            [Package(abspath("examples/simple_workspace/package_b"), self.workspace)],
            None,
        )

        self.assertEqual(
            self.workspace.resolve_label(Label("//package_b", None)), expected
        )

    def test_root(self):
        expected = [
            Package(abspath("examples/simple_workspace/package_a"), self.workspace),
            Package(abspath("examples/simple_workspace/package_b"), self.workspace),
            Package(
                abspath("examples/simple_workspace/nested/package_c"), self.workspace
            ),
        ]
        result = self.workspace.resolve_label(Label("//", "action"))

        # No order guarantee
        self.assertCountEqual(result.packages, expected)

    def test_parent(self):
        expected = ResolvedLabel(
            [
                Package(
                    abspath("examples/simple_workspace/nested/package_c"),
                    self.workspace,
                )
            ],
            Target("action"),
        )

        self.assertEqual(
            self.workspace.resolve_label(Label("//nested", "action")), expected
        )

    def test_no_package_with_active_package(self):
        # in self.run cd'ed into the package_c
        expected = ResolvedLabel(
            [
                Package(
                    abspath("examples/simple_workspace/nested/package_c"),
                    self.workspace,
                )
            ],
            Target("action"),
        )

        self.assertEqual(self.workspace.resolve_label(Label(None, "action")), expected)

    def test_no_package_and_no_active_package(self):
        with cd(abspath("examples/simple_workspace/non_package")):
            with self.assertRaises(PackageNotFound):
                self.workspace.resolve_label(Label(None, "action"))

    def test_relative_package(self):
        expected = ResolvedLabel(
            [
                Package(
                    abspath("examples/simple_workspace/nested/package_c"),
                    self.workspace,
                )
            ],
            Target("action"),
        )
        with cd(abspath("examples/simple_workspace/nested")):
            self.assertEqual(
                self.workspace.resolve_label(Label("package_c", "action")), expected
            )

    def test_relative_package_not_found(self):
        with cd(abspath("examples/simple_workspace/nested")):
            with self.assertRaises(PackageNotFound):
                # package_a is sibling, not child of this folder, so
                # we won't find it
                self.workspace.resolve_label(Label("package_a", "action"))


class WorkspaceResolveLabelPathTest(TestCase):
    def setUp(self):
        self.workspace = example_workspace()

    def tearDown(self):
        del self.workspace

    def run(self, result=None):
        # Run these resolve tests from a specific location inside the workspace
        # to ensure that the cwd is used as the active_package when needed and
        # no other time.
        with cd(abspath("examples/simple_workspace/nested/package_c")):
            super().run(result=result)

    def test_package_b(self):
        expected = Package(
            abspath("examples/simple_workspace/package_b"),
            self.workspace,
        )
        self.assertEqual(self.workspace.resolve_label_path("//package_b"), expected)

    def test_workspace(self):
        with self.assertRaises(PackageNotFound):
            self.workspace.resolve_label_path("//")

    def test_package_parent(self):
        with self.assertRaises(PackageNotFound):
            self.workspace.resolve_label_path("//nested")

    def test_package_subdir(self):
        with self.assertRaises(PackageNotFound):
            self.workspace.resolve_label_path("//package_b/x")


class WorkspaceReadTest(TestCase):
    def setUp(self):
        self.workspace = example_workspace()

    def tearDown(self):
        del self.workspace

    def test_path_exists(self):
        self.assertTrue(self.workspace.path_exists("WORKSPACE.toml"))
        self.assertTrue(self.workspace.path_exists("package_a"))
        self.assertFalse(self.workspace.path_exists("does_not_exist"))

    def test_read_toml_workspace(self):
        expected = {"workspace": {"example": "foo"}}
        self.assertEqual(self.workspace.read_toml("WORKSPACE.toml"), expected)

    def test_read_toml_nested(self):
        expected = {"package": {"runtimes": ["python"]}}
        self.assertEqual(
            self.workspace.read_toml(Path("package_b/BUILD.toml")), expected
        )
