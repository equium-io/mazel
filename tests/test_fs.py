from pathlib import Path
from unittest import TestCase

from mazel.fs import cd

from .utils import abspath


def cwd():
    return Path.cwd()


class CdTest(TestCase):
    def setUp(self):
        self.current_dir = abspath("..")  # tests run from package root
        self.other_dir = abspath("examples/simple_workspace")

    def test_cd(self):
        self.assertEqual(cwd(), self.current_dir)
        with cd(abspath("examples/simple_workspace")):
            self.assertEqual(cwd(), self.other_dir)

        self.assertEqual(cwd(), self.current_dir)

    def test_failure(self):
        try:
            with cd(abspath("examples/simple_workspace")):
                self.assertEqual(cwd(), self.other_dir)
                raise Exception()

            self.fail("unreachable")
        except Exception:
            pass

        self.assertEqual(cwd(), self.current_dir)

    def test_expand_home(self):
        with cd("~"):
            self.assertEqual(cwd(), Path.home())
