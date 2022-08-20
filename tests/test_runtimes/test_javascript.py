import json

from mazel.runtimes import JavascriptRuntime

from ..test_package import make_package
from .utils import RuntimeTestCase

EXAMPLE_PACKAGE_JSON = {
    "dependencies": {"react": "^16.13.1", "package_b": "file:../package_b"},
    "devDependencies": {
        "@babel/core": "^7.9.6",
        "package_c": "file:../nested/package_c",
    },
}


class JavascriptRuntimeTest(RuntimeTestCase):
    runtime_cls = JavascriptRuntime

    def test_runtime_label(self):
        runtime = self.make_runtime()
        self.assertEqual(runtime.runtime_label, "javascript")

    def test_package_json(self):
        runtime = self.make_runtime()

        runtime.package.read_path.return_value = json.dumps(EXAMPLE_PACKAGE_JSON)

        # call multiple times, ensure it is cached, not re-read
        self.assertEqual(runtime.package_json, runtime.package_json)

        runtime.package.read_path.assert_called_once_with("package.json")

    def test_dependencies(self):
        runtime = self.make_runtime()

        runtime.package.read_path.return_value = json.dumps(EXAMPLE_PACKAGE_JSON)

        deps = runtime.dependencies()
        self.assertEqual(
            deps,
            {"react": "^16.13.1", "package_b": "file:../package_b"},
        )

    def test_dev_dependencies(self):
        runtime = self.make_runtime()

        runtime.package.read_path.return_value = json.dumps(EXAMPLE_PACKAGE_JSON)

        deps = runtime.dev_dependencies()
        self.assertEqual(
            deps, {"@babel/core": "^7.9.6", "package_c": "file:../nested/package_c"}
        )

    def test_workspace_dependencies(self):
        package = make_package("examples/simple_workspace/package_a")
        runtime = self.make_runtime(package)

        runtime.package_json = EXAMPLE_PACKAGE_JSON
        pkgs = runtime.workspace_dependencies()

        self.assertCountEqual(
            pkgs,
            [
                make_package("examples/simple_workspace/package_b"),
                make_package("examples/simple_workspace/nested/package_c"),
            ],
        )
