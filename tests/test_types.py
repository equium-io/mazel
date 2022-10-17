from unittest import TestCase

from mazel.types import Commit, CommitRange


class CommitRangeTest(TestCase):
    def test_parse_pair(self):
        rev = CommitRange.parse("39fc076..92c469d")

        self.assertEqual(rev, CommitRange(Commit("39fc076"), Commit("92c469d")))

    def test_parse_single(self):
        rev = CommitRange.parse("39fc076")

        self.assertEqual(rev, CommitRange(Commit("39fc076"), Commit("HEAD")))
