from unittest import TestCase
from unittest.mock import create_autospec

from mazel.exceptions import RuntimeNotFound
from mazel.package import Package
from mazel.runtimes import (
    DockerRuntime,
    GoRuntime,
    JavascriptRuntime,
    MeteorRuntime,
    PythonRuntime,
    Runtime,
)


class RuntimeTest(TestCase):
    def test_runtime_implementations(self):
        self.assertCountEqual(
            Runtime.implementations(),
            [DockerRuntime, GoRuntime, JavascriptRuntime, MeteorRuntime, PythonRuntime],
        )

    def test_resolve(self):
        package = create_autospec(Package)
        runtime = Runtime.resolve("python", package)

        self.assertIsInstance(runtime, PythonRuntime)
        self.assertEqual(runtime.package, package)

    def test_resolve_not_found(self):
        package = create_autospec(Package)
        with self.assertRaises(RuntimeNotFound):
            Runtime.resolve("badruntime", package)
