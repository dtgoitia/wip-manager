import pytest

from src.graph import Graph, GraphError, Node, NodeId

# def test_node_has_parent():
#     node = Node(parents=[NodeId("parent_a")])
#     assert node.has_parents is True


# def test_node_has_no_parents():
#     node = Node(parents=[])
#     assert node.has_parents is False


# def test_graph_is_initialized_with_a_single_node():
#     node = Node(id=NodeId("p1"), parents=[], children=[])
#     graph = Graph(first_node=node)
#     assert graph


# @pytest.fixture
# def graph() -> Graph:
#     node = Node(id=NodeId("first_node"))
#     graph = Graph(first_node=node)
#     return graph


def test_add_first_node_to_graph():
    node = Node(id=NodeId("foo"))
    graph = Graph(first_node=node)
    assert graph.nodes == {node.id: node}


def test_graph_add_child():
    first = Node(id=NodeId("first_node"))
    graph = Graph(first_node=first)
    child = Node(id=NodeId("child"))
    graph.add_child(parent=first, child=child)
    assert graph.nodes == {first.id: first, child.id: child}
    assert graph.parents_per_node == {
        first.id: frozenset(),
        child.id: frozenset({first.id}),
    }
    assert graph.children_per_node == {
        first.id: frozenset({child.id}),
        child.id: frozenset(),
    }


def test_graph_add_parent():
    first = Node(id=NodeId("first_node"))
    graph = Graph(first_node=first)
    parent = Node(id=NodeId("parent"))
    graph.add_parent(parent=parent, child=first)
    assert graph.nodes == {first.id: first, parent.id: parent}
    assert graph.parents_per_node == {
        first.id: frozenset({parent.id}),
        parent.id: frozenset(),
    }
    assert graph.children_per_node == {
        first.id: frozenset(),
        parent.id: frozenset({first.id}),
    }


def test_graph_raises_if_parent_is_missing_when_adding_a_child():
    parent = Node(id=NodeId("parent"))
    missing = Node(id=NodeId("missing"))
    child = Node(id=NodeId("child"))
    graph = Graph(first_node=parent)

    with pytest.raises(GraphError) as e:
        graph.add_child(parent=missing, child=child)

    exc = e.value

    assert exc.args == ("Node #missing not in graph, cannot receive a child node",)


def test_graph_raises_if_child_is_missing_when_adding_a_parent():
    parent = Node(id=NodeId("parent"))
    missing = Node(id=NodeId("missing"))
    child = Node(id=NodeId("child"))
    graph = Graph(first_node=parent)

    with pytest.raises(GraphError) as e:
        graph.add_parent(parent=child, child=missing)

    exc = e.value

    assert exc.args == ("Node #missing not in graph, cannot receive a parent node",)
