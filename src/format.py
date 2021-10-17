import itertools
import re
from dataclasses import replace
from pathlib import Path

from src.interpreter import items_to_markdown, parse_document
from src.io import read_markdown_file, write_text_file
from src.types import ExternalReference, Item, Task, TaskDetail

TASK_HAS_HYPERLINK = re.compile(r"\[[^\[\]]{2,}\]\(([^\(\)]*)\)")
TASK_DETAIL_HAS_HYPERLINK = re.compile(r"\[[^\[\]]{2,}\]\(([^\(\)]*)\)")

EXTERNAL_REFERENCE_DEFAULT_DESCRIPTION = "?"


def add_eof_new_line(*, path: Path) -> None:
    lines = path.read_text().split("\n")
    last_line = lines[-1]
    empty_line = ""
    if last_line != empty_line:
        lines.append(empty_line)
    path.write_text("\n".join(lines))


def tidy_up_external_references(*, path: Path) -> None:
    original_content = read_markdown_file(path=path)
    items = parse_document(original_content)

    external_refs = [item for item in items if isinstance(item, ExternalReference)]
    last_external_reference = external_refs[-1]
    new_numbers = itertools.count(last_external_reference.number + 1)

    new_external_references = []

    def process(item: Item) -> Item:
        if not isinstance(item, Task):
            return item

        task = item

        # process the task description
        hyperlinks = TASK_HAS_HYPERLINK.findall(task.description)
        task_needs_processing = bool(hyperlinks)

        new_description = task.description
        if task_needs_processing:
            for path in hyperlinks:
                number = next(new_numbers)
                new_description = new_description.replace(f"({path})", f"[{number}]")
                external_reference = ExternalReference(
                    number=number,
                    path=path,
                    description=EXTERNAL_REFERENCE_DEFAULT_DESCRIPTION,
                )
                new_external_references.append(external_reference)

        # process the task details
        processed_details = []
        for detail in task.details:
            details_hyperlinks = TASK_DETAIL_HAS_HYPERLINK.findall(detail.description)
            new_detail_desc = detail.description
            for path in details_hyperlinks:
                number = next(new_numbers)
                new_detail_desc = new_detail_desc.replace(f"({path})", f"[{number}]")
                external_reference = ExternalReference(
                    number=number,
                    path=path,
                    description=EXTERNAL_REFERENCE_DEFAULT_DESCRIPTION,
                )
                new_external_references.append(external_reference)
            processed_detail = TaskDetail(description=new_detail_desc)
            processed_details.append(processed_detail)

        processed_task = replace(
            task,
            description=new_description,
            details=processed_details,
        )

        return processed_task

    processed_items = [process(item) for item in items]

    # insert new external references before the EOF new line
    last_item = processed_items.pop()
    processed_items.extend([*new_external_references, last_item])
    processed_content = items_to_markdown(processed_items)

    write_text_file(path=path, content=processed_content)
