from mazel.runtimes import DockerRuntime

from .utils import RuntimeTestCase


class DockerRuntimeTest(RuntimeTestCase):
    runtime_cls = DockerRuntime

    def test_runtime_label(self):
        runtime = self.make_runtime()
        self.assertEqual(runtime.runtime_label, "docker")

    def test_workspace_dependencies(self):
        runtime = self.make_runtime()
        # TODO Actually implement
        self.assertEqual(list(runtime.workspace_dependencies()), [])
