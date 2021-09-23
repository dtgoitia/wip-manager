from collections import defaultdict
from pprint import pprint
from typing import Dict, Iterable, Iterator, List

from pytest import Item

from src.hash import Hash
from src.types import Task

AFTER = "after"  # current task must be done #r:after-xxxxxx
BEFORE = "before"  # current task must be done #r:before-xxxxxx


def assert_completed_tasks_have_no_pending_prior_task(items: Iterable[Item]) -> None:
    tasks = [item for item in items if isinstance(item, Task)]

    completed_items_hashes = set()
    incomplete_items_hashes = set()
    for task in tasks:
        if task.done:
            completed_items_hashes.add(task.hash)
        else:
            incomplete_items_hashes.add(task.hash)

    relations_graph = get_interdependency_graph(tasks)

    def previous_tasks_are_completed(graph, node) -> bool:
        if node not in graph:
            # this node doesn't appear in any interdependency relationship
            yield True
            return

        # get hashes of the tasks that need to be done AFTER `node`
        previous_hashes = graph[node][AFTER]
        for previous_hash in previous_hashes:
            print(f"  prev {previous_hash} is complete", end="")
            if previous_hash in incomplete_items_hashes:
                print("  False")
                yield False  # an incomplete item found, no need to keep traversing
            else:
                # all tasks checked so far are completed, so good, keep on
                print("  True")
                yield True
                yield from previous_tasks_are_completed(graph, previous_hash)

    for completed_hash in completed_items_hashes:
        print(f"Checking {completed_hash}:")
        previous_tasks_done = all(
            previous_tasks_are_completed(relations_graph, completed_hash)
        )
        print(f"  task {completed_hash}, previous tasks done: {previous_tasks_done}")

    # for completed_task

    breakpoint()
    print("")


TaskGraph = Dict[Hash, Dict[str, List[Hash]]]


def get_interdependency_graph(tasks: Iterable[Task]) -> TaskGraph:
    # find parents per task
    def _clean_node_factory():
        return {AFTER: [], BEFORE: []}

    relations_graph = defaultdict(_clean_node_factory)
    """
    1   2     MUST BE DONE BEFORE (prior)
     \ /
      3   5
       \ /
        4     MUST BE DONE AFTER (later)
    prior_task_per_task = {
        1: {"prior": [], "later": []},
        2: {"prior": [], "later": []},
        3: {"prior": [], "later": []},
        4: {"prior": [], "later": []},
        5: {"prior": [], "later": []},
    }
    """
    for task in tasks:
        current = task.hash
        relations = [tag for tag in task.tags if tag.type == "r"]
        for relation in relations:
            relation_type, subject = relation.value.split("-")
            if relation_type == AFTER:
                # current task must be done after `subject`
                previous = subject
                relations_graph[current][AFTER].append(previous)
                relations_graph[previous][BEFORE].append(current)
                # pprint(relations_graph)
            elif relation_type == BEFORE:
                later = subject
                relations_graph[later][AFTER].append(current)
                relations_graph[current][BEFORE].append(later)
                # pprint(relations_graph)
            else:
                raise NotImplementedError("I didn't expect to reach here!")

    task_grah: TaskGraph = {}
    for node, connections in relations_graph.items():
        task_grah[node] = {**connections}

    return task_grah
