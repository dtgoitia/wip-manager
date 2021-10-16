from pathlib import Path

from src.interpreter import parse_document
from src.io import read_markdown_file
from src.types import Tag, TagValue, Task

GroupName = TagValue


def filter_wip_file(path: Path, by_group: GroupName) -> None:
    group_tag = Tag(type="g", value=by_group)

    original_content = read_markdown_file(path=path)
    items = parse_document(original_content)

    tasks = (item for item in items if isinstance(item, Task))
    tasks_in_group = (task for task in tasks if group_tag in task.tags)
    todo_tasks = (task for task in tasks_in_group if not task.done)

    for task in todo_tasks:
        assert isinstance(task, Task)
        print(format_task(task))


def format_task(task: Task) -> str:
    return "\n".join(
        [
            f"- [ ] {task.description}",
            *[detail.to_str() for detail in task.details],
        ]
    )
