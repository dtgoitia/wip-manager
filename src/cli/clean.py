from pathlib import Path
from typing import List

from src.io import append_to_archive, read_markdown_file, write_text_file
from src.types import (
    MarkdownStr,
    Task,
    deserialize_content,
    parse_items,
    separate_completed_items,
)


def archive_completed_tasks(*, path: Path, archive_path: Path) -> None:
    # TODO: add a function to handle tag creation
    original_content = read_markdown_file(path=path)
    items = parse_items(original_content)
    completed_items, remaining_items = separate_completed_items(items)

    # Update task archive
    archived_tasks_as_str = serialize_completed_tasks(completed_tasks=completed_items)
    append_to_archive(path=archive_path, content=archived_tasks_as_str)

    # Update WIP file
    updated_content = deserialize_content(remaining_items)
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
