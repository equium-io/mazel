from mazel.runtimes import PythonRuntime

from ..test_package import make_package
from .utils import RuntimeTestCase

# Pre-parsed toml
EXAMPLE_PYPROJECT = {
    "tool": {
        "poetry": {
            "dependencies": {
                "python": "~3.7",
                "pandas": "~0.25.3",
                "package_b": {"path": "../package_b"},
            },
            "dev-dependencies": {
                "testlib": "~1.0.0",
                "package_c": {"path": "../nested/package_c"},
            },
        }
    }
}


class PythonRuntimeTest(RuntimeTestCase):
    runtime_cls = PythonRuntime

    def test_runtime_label(self):
        runtime = self.make_runtime()
        self.assertEqual(runtime.runtime_label, "python")

    def test_pyproject_toml(self):
        runtime = self.make_runtime()

        # call multiple times, ensure it is cached, not re-read
        self.assertIs(runtime.pyproject_toml, runtime.pyproject_toml)

        runtime.package.read_toml.assert_called_once_with("pyproject.toml")

    def test_dependencies(self):
        runtime = self.make_runtime()

        runtime.package.read_toml.return_value = EXAMPLE_PYPROJECT

        deps = runtime.dependencies()
        self.assertEqual(
            deps,
            {
                "python": "~3.7",
                "pandas": "~0.25.3",
                "package_b": {"path": "../package_b"},
            },
        )

    def test_dev_dependencies(self):
        runtime = self.make_runtime()

        runtime.package.read_toml.return_value = EXAMPLE_PYPROJECT

        deps = runtime.dev_dependencies()
        self.assertEqual(
            deps, {"testlib": "~1.0.0", "package_c": {"path": "../nested/package_c"}}
        )

    def test_workspace_dependencies(self):
        package = make_package("examples/simple_workspace/package_a")
        runtime = self.make_runtime(package)

        runtime.pyproject_toml = EXAMPLE_PYPROJECT
        pkgs = runtime.workspace_dependencies()

        self.assertCountEqual(
            pkgs,
            [
                make_package("examples/simple_workspace/package_b"),
                make_package("examples/simple_workspace/nested/package_c"),
            ],
        )
