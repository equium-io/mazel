from unittest import TestCase
from unittest.mock import create_autospec

from mazel.package import Package


class RuntimeTestCase(TestCase):
    runtime_cls = None

    def make_runtime(self, package=None):
        if package is None:
            package = create_autospec(Package)
        return self.runtime_cls(package)
