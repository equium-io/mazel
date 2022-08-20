from mazel.runtimes import GoRuntime

from .utils import RuntimeTestCase


class JavascriptRuntimeTest(RuntimeTestCase):
    runtime_cls = GoRuntime

    def test_runtime_label(self):
        runtime = self.make_runtime()
        self.assertEqual(runtime.runtime_label, "go")

    def test_workspace_dependencies(self):
        runtime = self.make_runtime()
        # TODO Actually implement
        self.assertEqual(list(runtime.workspace_dependencies()), [])
