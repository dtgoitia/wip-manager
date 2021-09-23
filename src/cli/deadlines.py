import datetime
from pathlib import Path

from src.interpreter import parse_document
from src.io import read_markdown_file
from src.types import Task


def show_tasks_sorted_by_deadline(path: Path) -> None:
    original_content = read_markdown_file(path=path)
    items = parse_document(original_content)

    tasks = (item for item in items if isinstance(item, Task))
    tasks_with_deadlines = [task for task in tasks if task.deadline]

    def criteria(task):
        # earliest deadlines first, completed first
        return task.deadline, not task.done

    today = datetime.date.today()
    for task in sorted(tasks_with_deadlines, key=criteria):
        assert task.deadline, "Oops! I expected to have a date here :S"
        delta = task.deadline - today
        days_left = delta.days
        print(f"{days_left} days", task.to_str())
