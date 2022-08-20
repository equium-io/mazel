from unittest import TestCase

from mazel.label import Label, ResolvedLabel, Target
from mazel.package import Package

from .utils import abspath, example_workspace


class LabelTest(TestCase):
    def test_parse_root(self):
        self.assertEqual(Label.parse("//"), Label("//", None))

    def test_parse_none(self):
        self.assertEqual(Label.parse(None), Label(None, None))

    def test_parse_full(self):
        self.assertEqual(
            Label.parse("//tools/app:action"), Label("//tools/app", "action")
        )

    def test_parse_relative_package(self):
        self.assertEqual(Label.parse("app:action"), Label("app", "action"))

    def test_parse_only_package(self):
        self.assertEqual(Label.parse("//tools/app"), Label("//tools/app", None))

    def test_parse_only_package_with_separator(self):
        # Not sure this is a valid bazel identifier
        self.assertEqual(Label.parse("//tools/app:"), Label("//tools/app", None))

    def test_parse_only_target(self):
        self.assertEqual(Label.parse(":action"), Label(None, "action"))

    def test_parse_only_target_without_separator(self):
        self.assertEqual(Label.parse("action"), Label(None, "action"))

    def test_is_absolute(self):
        self.assertTrue(Label.is_absolute("//tools/app"))
        self.assertTrue(Label.is_absolute("//"))
        self.assertFalse(Label.is_absolute("tools/app"))

    def test_str(self):
        self.assertEqual(str(Label("//tools/app", "action")), "//tools/app:action")
        self.assertEqual(str(Label("//tools/app", None)), "//tools/app:")
        self.assertEqual(str(Label(None, "action")), ":action")

    def test_repr(self):
        self.assertEqual(
            repr(Label("//tools/app", "action")), "<Label: //tools/app:action>"
        )


class ResolvedLabelTest(TestCase):
    def test_str(self):
        rl = ResolvedLabel(
            [
                Package(
                    abspath("examples/simple_workspace/package_a"),
                    example_workspace(),
                )
            ],
            Target("action"),
        )
        self.assertEqual(str(rl), "[<Package: package_a>]:action")

    def test_repr(self):
        rl = ResolvedLabel(
            [
                Package(
                    abspath("examples/simple_workspace/package_a"),
                    example_workspace(),
                )
            ],
            Target("action"),
        )
        self.assertEqual(repr(rl), "<ResolvedLabel: [<Package: package_a>]:action>")


class TargetTest(TestCase):
    def test_eq(self):
        self.assertTrue(Target("a") == Target("a"))
        self.assertFalse(Target("a") != Target("a"))

        self.assertFalse(Target("a") == Target("b"))
        self.assertTrue(Target("a") != Target("b"))

        self.assertTrue(Target(None) == Target(None))

        self.assertFalse(Target("a") == None)  # noqa

    def test_str(self):
        self.assertEqual(str(Target("action")), "action")

    def test_repr(self):
        self.assertEqual(repr(Target("action")), "<Target: action>")
