from pathlib import Path
from typing import List, Tuple

from src.interpreter import items_to_markdown, parse_document
from src.io import append_to_archive, read_markdown_file, write_text_file
from src.types import Item, MarkdownStr, Task


def archive_completed_tasks(*, path: Path, archive_path: Path) -> None:
    # TODO: add a function to handle tag creation
    original_content = read_markdown_file(path=path)
    items = parse_document(original_content)
    completed_items, remaining_items = separate_completed_items(items)

    # Update task archive
    archived_tasks_as_str = serialize_completed_tasks(completed_tasks=completed_items)
    append_to_archive(path=archive_path, content=archived_tasks_as_str)

    # Update WIP file
    updated_content = items_to_markdown(remaining_items)
    write_text_file(path=path, content=updated_content)

    # Report
    archived_items_amount = len(completed_items)
    print(f"Archived items: {archived_items_amount}")


def serialize_completed_tasks(completed_tasks: List[Task]) -> MarkdownStr:
    archived_items = [completed_to_archived_task(task=task) for task in completed_tasks]
    serialized_archived_items = "\n".join(archived_items)
    return serialized_archived_items


def completed_to_archived_task(task: Task) -> MarkdownStr:
    # TODO: consider if it's worth changing the format
    return task.to_str()


def separate_completed_items(items: List[Item]) -> Tuple[List[Task], List[Item]]:
    """Collect completed tasks and return them together with remaining tasks."""
    completed_tasks: List[Task] = []
    remainig_items: List[Item] = []

    for item in items:
        if isinstance(item, Task) and item.done:
            completed_task = item
            completed_tasks.append(completed_task)
        else:
            remainig_items.append(item)

    return completed_tasks, remainig_items
