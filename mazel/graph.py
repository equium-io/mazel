from typing import Any, Callable, Dict, Iterable, List, Set

from .package import Package

NodeApply = Callable[["Node", int], Any]  # Tried to use TypeVar instead of Any


def identity(node: "Node", level: int = 0) -> "Package":
    return node.package


# def bfs_recurse(
#     nodes: List["Node"], apply_fn: NodeApply, level: int = 0
# ) -> Iterable[Any]:
#     """Breadth-first recursion thru nodes, then each node's children"""
#     nodes = sorted(nodes, key=lambda node: node.package.label_path)
#     # First this level
#     for node in nodes:
#         yield apply_fn(node, level)

#     # Then the children
#     for node in nodes:
#         for result in bfs_recurse(node.children, apply_fn, level + 1):
#             yield result


# def dfs_recurse(
#     nodes: List["Node"], apply_fn: NodeApply, level: int = 0
# ) -> Iterable[Any]:
#     nodes = sorted(nodes, key=lambda node: node.package.label_path)
#     for node in nodes:
#         yield apply_fn(node, level)

#         for result in dfs_recurse(node.children, apply_fn, level + 1):
#             yield result


class Node(object):
    def __init__(
        self,
        package: Package,
        parents: List["Node"] = None,
        children: List["Node"] = None,
    ):
        self.package = package
        self.parents: List["Node"] = parents or []
        self.children: List["Node"] = children or []

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.package.label_path}>"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, self.__class__)
            and self.package == other.package
            # Node equality NOT a function of parents / children
            # and self.parents == other.parents
            # and self.children == other.children
        )

    def __hash__(self) -> int:
        return hash(self.package)


class PackageGraph(object):
    """Directed Graph for representing dependencies between Packages"""

    def __init__(self, nodes: Dict[Package, Node]):
        self._nodes = nodes

    @classmethod
    def from_packages(cls, packages: List[Package]) -> "PackageGraph":
        # Compute the graph by scanning thru the packages 3 times:

        # Scan 1) Generate Nodes from the packages
        nodes = {package: Node(package) for package in packages}

        # Scan 2) Find the depends on relationships that are the parents
        for node in nodes.values():
            for dep in node.package.depends_on():
                # TODO Deduplicate or warn on duplicates
                node.parents.append(nodes[dep])

        # Scan 3) Compute the children dependencies from the parents
        for node in nodes.values():
            for parent in node.parents:
                parent.children.append(node)

        # TODO validate that there are no circular references

        return cls(nodes)

    def invert(self) -> "PackageGraph":
        nodes = {
            package: Node(node.package, parents=node.children, children=node.parents)
            for package, node in self._nodes.items()
        }
        return PackageGraph(nodes)

    def nodes(self) -> List[Node]:
        return list(self._nodes.values())

    # def walk(
    #     self, apply_fn: NodeApply = identity, breadth_first: bool = True,
    # ) -> Iterable[Any]:
    #     recurse_fn = bfs_recurse if breadth_first else dfs_recurse

    #     # TODO options: include_mazel=False
    #     roots = [node for node in self.nodes() if not node.parents]
    #     return (node for node in recurse_fn(roots, apply_fn))

    def consume_tree(self, apply_fn: NodeApply = identity) -> Iterable[Any]:
        """
        Walk the graph, running apply_fn to each node, such that are parents are
        consumed before their children.
        """
        # WARNING: Inefficient: we are looping multiple times over all remaining Nodes
        #   - Can we use the BFS or DFS approaches to more intelligently walk the tree?
        #   - Alternatively could try to sort more intelligently, e.g libs before tools,
        #     though that is specific to our repo layout.
        #   - Could also look for roots for the first round.
        # WARNING: Non-deterministic ordering with Set looping & casting to list.
        #   Will result in differing execution times.

        consumed: Set[Node] = set()
        remaining: Set[Node] = set(self.nodes())
        level = -1
        while len(remaining) > 0:
            level += 1
            # cast to a list since we are going to modify the set in place (instead
            # of creating a new set, copying, and reassigning).
            for node in list(remaining):
                if len(set(node.parents) - consumed) == 0:
                    consumed.add(node)
                    remaining.remove(node)
                    result = apply_fn(node, level)

                    # Allow apply_func to return an iterable result that we will unroll
                    # via the `yield from`. But if not iterable, just return the single
                    # value
                    try:
                        yield from result
                    except TypeError:
                        yield result
