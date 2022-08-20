import random
from unittest import TestCase
from unittest.mock import create_autospec

from mazel.graph import Node, PackageGraph
from mazel.package import Package

from .test_package import make_package


class NodeTest(TestCase):
    def test_repr(self):
        package = create_autospec(Package)
        package.label_path = "//foo/bar"

        self.assertEqual(repr(Node(package)), "<Node: //foo/bar>")

    def test_eq(self):
        one = make_package("examples/simple_workspace/package_a")
        two = make_package("examples/simple_workspace/package_b")

        self.assertTrue(Node(one) == Node(one))
        self.assertTrue(Node(one) != Node(two))

        self.assertTrue(
            Node(one, children=[Node(two)]) == Node(one, children=[Node(two)])
        )
        self.assertTrue(
            Node(one, parents=[Node(two)]) == Node(one, parents=[Node(two)])
        )

        # parents / children do not play into Node equality, it is simply a container
        # to uniquely identify a Package
        self.assertTrue(Node(one) == Node(one, children=[Node(two)]))
        self.assertTrue(Node(one) == Node(one, parents=[Node(two)]))

    def test_hash(self):
        one = make_package("examples/simple_workspace/package_a")
        two = make_package("examples/simple_workspace/package_b")

        self.assertEqual(hash(Node(one)), hash(Node(one)))
        self.assertNotEqual(hash(Node(one)), hash(Node(two)))

        # for now, we don't hash by parents/children, since the only workflow is after
        # calling graph.invert(), and we don't expect to need to hash nodes from a
        # graph vs it's inversion
        self.assertEqual(hash(Node(one)), hash(Node(one, children=[Node(two)])))
        self.assertEqual(
            hash(Node(one, parents=[Node(two)])), hash(Node(one, children=[Node(two)]))
        )


class WalkLogger(object):
    def __init__(self):
        self.steps = []

    def __call__(self, node, level):
        self.steps.append((node, level))
        return len(self.steps)


class PackageGraphTest(TestCase):
    def setUp(self):
        self.pkg_one = create_autospec(Package)
        self.pkg_two = create_autospec(Package)
        self.pkg_two.depends_on.return_value = [self.pkg_one]
        self.pkg_three = create_autospec(Package)
        self.pkg_three.depends_on.return_value = [self.pkg_one, self.pkg_two]

    def test_from_package(self):
        pkg_one, pkg_two, pkg_three = self.pkg_one, self.pkg_two, self.pkg_three

        graph = PackageGraph.from_packages([pkg_one, pkg_two, pkg_three])

        self.assertCountEqual(graph._nodes.keys(), [pkg_one, pkg_two, pkg_three])

        self.assertCountEqual(graph._nodes[pkg_one].parents, [])
        self.assertCountEqual(
            graph._nodes[pkg_one].children, [Node(pkg_two), Node(pkg_three)]
        )

        self.assertCountEqual(graph._nodes[pkg_two].parents, [Node(pkg_one)])
        self.assertCountEqual(graph._nodes[pkg_two].children, [Node(pkg_three)])

        self.assertCountEqual(
            graph._nodes[pkg_three].parents, [Node(pkg_one), Node(pkg_two)]
        )
        self.assertCountEqual(graph._nodes[pkg_three].children, [])

    def test_invert(self):
        pkg_one, pkg_two, pkg_three = self.pkg_one, self.pkg_two, self.pkg_three

        original = PackageGraph.from_packages([pkg_one, pkg_two, pkg_three])

        graph = original.invert()

        self.assertIsNot(graph, original)

        self.assertCountEqual(graph._nodes.keys(), [pkg_one, pkg_two, pkg_three])

        self.assertCountEqual(
            graph._nodes[pkg_one].parents, [Node(pkg_two), Node(pkg_three)]
        )
        self.assertCountEqual(graph._nodes[pkg_one].children, [])

        self.assertCountEqual(graph._nodes[pkg_two].parents, [Node(pkg_three)])
        self.assertCountEqual(graph._nodes[pkg_two].children, [Node(pkg_one)])

        self.assertCountEqual(graph._nodes[pkg_three].parents, [])
        self.assertCountEqual(
            graph._nodes[pkg_three].children, [Node(pkg_one), Node(pkg_two)]
        )

    def test_consume_tree(self):
        pkg_one, pkg_two, pkg_three = self.pkg_one, self.pkg_two, self.pkg_three

        # Shuffle since the order does not matter
        packages = [pkg_one, pkg_two, pkg_three]
        random.shuffle(packages)
        graph = PackageGraph.from_packages(packages)

        logger = WalkLogger()

        result = list(graph.consume_tree(logger))

        self.assertEqual(result, [1, 2, 3])
        self.assertEqual(
            [step[0] for step in logger.steps],
            [Node(pkg_one), Node(pkg_two), Node(pkg_three)],
        )

    def test_consume_tree_idenity(self):
        pkg_one, pkg_two, pkg_three = self.pkg_one, self.pkg_two, self.pkg_three

        # Shuffle since the order does not matter
        packages = [pkg_one, pkg_two, pkg_three]
        random.shuffle(packages)
        graph = PackageGraph.from_packages(packages)

        result = list(graph.consume_tree())

        self.assertEqual(result, [pkg_one, pkg_two, pkg_three])

    # def test_walk(self):
    #     self.fail("TODO walk()")
