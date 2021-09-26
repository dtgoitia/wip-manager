from dataclasses import dataclass
from typing import Dict, FrozenSet, List, NewType, Protocol

NodeId = NewType("NodeId", str)


class NodeLike(Protocol):
    id: NodeId


@dataclass
class Node:
    id: NodeId


#     parents: FrozenSet[NodeId]
#     children: FrozenSet[NodeId]

#     def has_parents(self) -> bool:
#         return bool(self.parents)

#     def has_children(self) -> bool:
#         return bool(self.children)


class GraphError(Exception):
    ...


class Graph:
    nodes: Dict[NodeId, NodeLike]
    parents_per_node: Dict[NodeId, FrozenSet[NodeId]]
    children_per_node: Dict[NodeId, FrozenSet[NodeId]]

    def __init__(self, *, first_node: NodeLike) -> None:
        self.nodes = dict()
        self.nodes[first_node.id] = first_node
        self.parents_per_node = {first_node.id: frozenset()}
        self.children_per_node = {first_node.id: frozenset()}

    def add_child(self, *, parent: NodeLike, child: NodeLike) -> None:
        if not self._is_node_in_graph(parent):
            error_msg = f"Node #{parent.id} not in graph, cannot receive a child node"
            raise GraphError(error_msg)

        self._add_node_if_missing(child)

        existing_parents = self.parents_per_node[child.id]
        self.parents_per_node[child.id] = existing_parents.union({parent.id})

        existing_children = self.children_per_node[parent.id]
        self.children_per_node[parent.id] = existing_children.union({child.id})

    def add_parent(self, *, child: NodeLike, parent: NodeLike) -> None:
        if not self._is_node_in_graph(child):
            error_msg = f"Node #{child.id} not in graph, cannot receive a parent node"
            raise GraphError(error_msg)

        self._add_node_if_missing(parent)

        existing_parents = self.parents_per_node[child.id]
        self.parents_per_node[child.id] = existing_parents.union({parent.id})

        existing_children = self.children_per_node[parent.id]
        self.children_per_node[parent.id] = existing_children.union({child.id})

    def _is_node_in_graph(self, node: NodeLike) -> bool:
        return node.id in self.nodes

    def _add_node_if_missing(self, node: NodeLike) -> None:
        if not self._is_node_in_graph(node):
            self.nodes[node.id] = node
            self.parents_per_node[node.id] = frozenset()
            self.children_per_node[node.id] = frozenset()
