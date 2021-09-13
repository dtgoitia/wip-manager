from dataclasses import replace
from pathlib import Path
from typing import List

from src.hash import create_new_hash
from src.interpreter import items_to_markdown, parse_document
from src.io import read_markdown_file
from src.types import Item, Task


def add_hashes_to_tasks(*, path: Path) -> None:
    original_content = read_markdown_file(path=path)
    items = parse_document(original_content)

    updated_items: List[Item] = []
    tasks = (item for item in items if isinstance(item, Task))
    existing_hashes = {task.hash for task in tasks if task.hash}

    for item in items:
        if not isinstance(item, Task):
            updated_items.append(item)
            continue

        task = item
        if task.hash:
            updated_items.append(item)
            continue

        new_hash = create_new_hash(existing=existing_hashes)
        updated_task = replace(task, hash=new_hash)
        updated_items.append(updated_task)

    updated_content = items_to_markdown(updated_items)

    path.write_text(updated_content)
