from mazel.runtimes import MeteorRuntime

from ..test_package import make_package
from .utils import RuntimeTestCase

EXAMPLE_PACKAGE_JSON = {
    "dependencies": {"react": "^16.13.1", "package_b": "file:../package_b"},
}


class MeteorRuntimeTest(RuntimeTestCase):
    runtime_cls = MeteorRuntime

    def setUp(self):
        self.package = make_package("examples/simple_workspace/package_a")

        # make a symlink package_a/packages/package_c to nested/package_c
        self.pkgs_dir = self.package.path.joinpath("packages")
        self.pkgs_dir.mkdir(exist_ok=True)

        self.pkg_link = self.pkgs_dir.joinpath("package_c")
        self.pkg_link.symlink_to(self.package.path.joinpath("../nested/package_c"))

        self.addCleanup(self.pkgs_dir.rmdir)
        self.addCleanup(self.pkg_link.unlink)

    def test_runtime_label(self):
        runtime = self.make_runtime()
        self.assertEqual(runtime.runtime_label, "meteor")

    def test_dependencies(self):
        runtime = self.make_runtime(self.package)

        deps = list(runtime.dependencies())
        self.assertEqual(
            deps,
            [make_package("examples/simple_workspace/nested/package_c")],
        )

    def test_workspace_dependencies(self):
        runtime = self.make_runtime(self.package)

        runtime.javascript_runtime.package_json = EXAMPLE_PACKAGE_JSON
        pkgs = runtime.workspace_dependencies()

        # Joins meteor with javascript runtimes
        self.assertCountEqual(
            pkgs,
            [
                make_package("examples/simple_workspace/package_b"),
                make_package("examples/simple_workspace/nested/package_c"),
            ],
        )
