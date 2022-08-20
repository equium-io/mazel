import signal
import subprocess
from contextlib import ExitStack
from datetime import datetime
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import call, create_autospec, patch

import click

from mazel.commands.label_common import (
    LabelRunner,
    MakeLabel,
    MakeLabelCaptureErrors,
    MakeLabelPassInterrupt,
    RunOrder,
    TargetHandler,
)
from mazel.fs import cd
from mazel.label import Target
from mazel.package import Package

from ..utils import abspath, example_workspace
from .utils import CommandTestCase


class LabelRunnerTest(CommandTestCase):
    def run(self, result=None):
        super().run(result=result)

    def setUp(self):
        super().setUp()
        self.handler = create_autospec(TargetHandler)

        self.workspace = example_workspace()

        self.package_a = Package(
            abspath("examples/simple_workspace/package_a"), self.workspace
        )
        self.package_b = Package(
            abspath("examples/simple_workspace/package_b"), self.workspace
        )
        self.package_c = Package(
            abspath("examples/simple_workspace/nested/package_c"), self.workspace
        )

    def tearDown(self):
        super().tearDown()
        del self.workspace

    def test_full_path_and_target(self):
        LabelRunner(self.handler, "fallback").run("//package_a:trgt")

        self.handler.handle.assert_called_once_with(
            self.package_a,
            Target("trgt"),
        )

    def test_multiple_packages(self):
        LabelRunner(self.handler, "fallback").run("//:trgt")

        self.handler.handle.assert_any_call(
            self.package_a,
            Target("trgt"),
        )
        self.handler.handle.assert_any_call(
            self.package_b,
            Target("trgt"),
        )
        self.handler.handle.assert_any_call(
            self.package_c,
            Target("trgt"),
        )

    def test_no_target(self):
        LabelRunner(self.handler, Target("fallback")).run("//package_a")

        self.handler.handle.assert_called_once_with(
            self.package_a,
            Target("fallback"),
        )

    def test_not_in_workspace(self):
        with TemporaryDirectory() as tmpdir:
            with cd(tmpdir):
                with self.assertRaises(click.ClickException):
                    LabelRunner(self.handler, Target("fallback")).run("//package_a")

    def test_collect_errors(self):
        self.handler.handle.side_effect = click.ClickException("error")

        # We still get the exception after all 3 packages get run
        with self.assertRaises(click.ClickException):
            LabelRunner(self.handler, Target("fallback")).run("//")

        # All 3 packages should get caled, even though each will produce an error
        self.assertEqual(self.handler.handle.call_count, 3)

    def test_run_order_single(self):
        LabelRunner(self.handler, "fallback").run("//package_a:trgt")

        self.handler.handle.assert_has_calls([call(self.package_a, Target("trgt"))])

    def test_run_order_multiple_ordered(self):
        LabelRunner(self.handler, "fallback", RunOrder.ORDERED).run("//:trgt")
        self.handler.handle.assert_has_calls(
            [
                call(self.package_c, Target("trgt")),
                call(self.package_b, Target("trgt")),
                call(self.package_a, Target("trgt")),
            ]
        )

    def test_run_order_multiple_reversed(self):
        LabelRunner(self.handler, "fallback", RunOrder.REVERSED).run("//:trgt")
        self.handler.handle.assert_has_calls(
            [
                call(self.package_a, Target("trgt")),
                call(self.package_b, Target("trgt")),
                call(self.package_c, Target("trgt")),
            ]
        )

    def test_run_order_multiple_unordered(self):
        LabelRunner(self.handler, "fallback", RunOrder.UNORDERED).run("//:trgt")
        self.handler.handle.assert_any_call(self.package_a, Target("trgt"))
        self.handler.handle.assert_any_call(self.package_b, Target("trgt"))
        self.handler.handle.assert_any_call(self.package_c, Target("trgt"))

    def test_run_with_ancestors(self):
        LabelRunner(
            self.handler, "fallback", RunOrder.ORDERED, with_ancestors=True
        ).run("//package_b:trgt")
        self.handler.handle.assert_has_calls(
            [
                call(self.package_c, Target("trgt")),
                call(self.package_b, Target("trgt")),
            ]
        )

    def test_run_with_descendants(self):
        LabelRunner(
            self.handler, "fallback", RunOrder.ORDERED, with_descendants=True
        ).run("//package_b:trgt")
        self.handler.handle.assert_has_calls(
            [
                call(self.package_b, Target("trgt")),
                call(self.package_a, Target("trgt")),
            ]
        )


class TargetHandlerTest(TestCase):
    def test_hande(self):
        with self.assertRaises(TypeError):
            # Abstract method
            TargetHandler().handle(None, None)


class MakeLabelTestCase(TestCase):
    def run(self, result=None):
        with ExitStack() as stack:
            self.mock_run = stack.enter_context(
                patch("mazel.commands.label_common.subprocess.run", autospec=True)
            )

            self.mock_target_exists = stack.enter_context(
                patch(
                    "mazel.commands.label_common.MakeLabel.target_exists", autospec=True
                )
            )
            self.mock_target_exists.return_value = True

            self.mock_secho = stack.enter_context(
                patch("mazel.commands.label_common.click.secho", autospec=True)
            )

            self.mock_datetime = stack.enter_context(
                patch("mazel.commands.label_common.datetime", autospec=True)
            )
            self.mock_datetime.now.return_value = datetime(2020, 4, 19, 12, 0)

            super().run(result=result)

    def setUp(self):
        super().setUp()
        self.workspace = example_workspace()

    def tearDown(self):
        super().tearDown()
        del self.workspace

    def call_handle(self, path):
        self.handler_cls().handle(Package(path, self.workspace), Target("test"))


class MakeLabelTest(MakeLabelTestCase):
    handler_cls = MakeLabel

    def test_run(self):
        path = abspath("examples/simple_workspace/package_b")

        self.call_handle(path)

        self.mock_run.assert_called_with(["make", "-s", "test"], cwd=path, check=True)
        self.mock_secho.assert_has_calls(
            [
                call("\u21D8 //package_b:test", fg="cyan"),
                call("\u2714 //package_b:test (Elapsed time: 0:00:00)", fg="green"),
            ]
        )

    def test_error(self):
        self.mock_run.side_effect = subprocess.CalledProcessError(2, "make ...")

        path = abspath("examples/simple_workspace/package_b")

        with self.assertRaises(click.ClickException):
            self.call_handle(path)

        self.mock_run.assert_called_with(["make", "-s", "test"], cwd=path, check=True)
        self.mock_secho.assert_has_calls(
            [
                call("\u21D8 //package_b:test", fg="cyan"),
                call(
                    "\u2718 //package_b:test (Elapsed time: 0:00:00)",
                    fg="red",
                    bold=True,
                ),
            ]
        )

    def test_target_not_exist(self):
        self.mock_target_exists.return_value = False
        path = abspath("examples/simple_workspace/package_b")

        self.call_handle(path)
        self.assertFalse(self.mock_run.called)
        self.assertFalse(self.mock_secho.called)


class MakeLabelCaptureErrorsTest(MakeLabelTestCase):
    handler_cls = MakeLabelCaptureErrors

    def test_run(self):
        path = abspath("examples/simple_workspace/package_b")

        self.call_handle(path)

        self.mock_run.assert_called_with(
            ["make", "-s", "test"],
            cwd=path,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.mock_secho.assert_has_calls(
            [
                call("\u21D8 //package_b:test", fg="cyan"),
                call("\u2714 //package_b:test (Elapsed time: 0:00:00)", fg="green"),
            ]
        )

    def test_error(self):
        self.mock_run.side_effect = subprocess.CalledProcessError(
            2, "make ...", output="foobar failure"
        )

        path = abspath("examples/simple_workspace/package_b")

        with self.assertRaises(click.ClickException):
            self.call_handle(path)

        self.mock_run.assert_called_with(
            ["make", "-s", "test"],
            cwd=path,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.mock_secho.assert_has_calls(
            [
                call("\u21D8 //package_b:test", fg="cyan"),
                call("foobar failure"),
                call(
                    "\u2718 //package_b:test (Elapsed time: 0:00:00)",
                    fg="red",
                    bold=True,
                ),
            ]
        )


class MakeLabelPassInterruptTest(MakeLabelTestCase):
    handler_cls = MakeLabelPassInterrupt

    def run(self, result=None):
        with patch(
            "mazel.commands.label_common.subprocess.Popen", autospec=True
        ) as self.mock_popen:
            # mocking a context manager ... gross
            self.mock_process = self.mock_popen.return_value.__enter__.return_value
            self.mock_process.wait.return_value = 0

            super().run(result)

    def test_run(self):
        path = abspath("examples/simple_workspace/package_b")

        self.call_handle(path)

        self.mock_popen.assert_called_with(["make", "-s", "test"], cwd=path)
        self.mock_secho.assert_has_calls(
            [
                call("\u21D8 //package_b:test", fg="cyan"),
                call("\u2714 //package_b:test (Elapsed time: 0:00:00)", fg="green"),
            ]
        )

    def test_error(self):
        self.mock_process.wait.return_value = 1

        path = abspath("examples/simple_workspace/package_b")

        with self.assertRaises(click.ClickException):
            self.call_handle(path)

        self.mock_popen.assert_called_with(["make", "-s", "test"], cwd=path)
        self.mock_secho.assert_has_calls(
            [
                call("\u21D8 //package_b:test", fg="cyan"),
                call(
                    "\u2718 //package_b:test (Elapsed time: 0:00:00)",
                    fg="red",
                    bold=True,
                ),
            ]
        )

    def test_sigint(self):
        # First call simulate a Ctrl-C, then normal exit, which is masked by the -SIGINT
        self.mock_process.wait.side_effect = [KeyboardInterrupt(), -signal.SIGINT]

        path = abspath("examples/simple_workspace/package_b")

        self.call_handle(path)

        self.mock_popen.assert_called_with(["make", "-s", "test"], cwd=path)
        self.mock_process.send_signal.assert_called_once_with(signal.SIGINT)


class TargetExistsTest(TestCase):
    def run(self, result=None):
        with patch(
            "mazel.commands.label_common.subprocess.run", autospec=True
        ) as self.mock_run:
            super().run(result=result)

    def setUp(self):
        super().setUp()
        self.workspace = example_workspace()

    def tearDown(self):
        super().tearDown()
        del self.workspace

    def test_exists(self):
        self.mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)

        path = abspath("examples/simple_workspace/package_b")

        self.assertTrue(
            MakeLabel().target_exists(Package(path, self.workspace), Target("test"))
        )
        self.mock_run.assert_called_with(
            ["make", "-n", "test"],
            cwd=path,
            capture_output=True,
            encoding="utf-8",
        )

    def test_not_exists(self):
        self.mock_run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=2,
            stderr="make: *** No rule to make target 'test'.  Stop.\n",
        )

        path = abspath("examples/simple_workspace/package_b")

        self.assertFalse(
            MakeLabel().target_exists(Package(path, self.workspace), Target("test"))
        )
        self.mock_run.assert_called_with(
            ["make", "-n", "test"],
            cwd=path,
            capture_output=True,
            encoding="utf-8",
        )
