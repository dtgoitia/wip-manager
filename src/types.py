from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Union, cast

MarkdownStr = str
TaskTag = str
JsonDict = Dict[str, Any]

INCOMPLETE_TASK_PREFIX = "- [ ] "
COMPLETED_TASK_PREFIX = "- [x] "
DETAIL_PREFIX = "  - "
_NO_DETAILS: List[TaskDetail] = []
TASK_TAG_PATTERN = re.compile(r"\s#([a-z]:[a-z0-9-_,]*)\s?")  # `#g:group1_b`
LINE_IS_TASK_PATTERN = re.compile(r"^- \[")  # starts with `- [ ] ` or `- [x] `
LINE_IS_DETAIL_PATTERN = re.compile(r"^  - ")  # starts with `  - `
LINE_IS_EXTERNAL_REFERENCE_PATTERN = re.compile(r'\[([0-9]+)\]: ([^\s]+)\s"(.*)"$')


@dataclass
class Task:
    description: str
    done: bool
    details: List[TaskDetail]
    tags: List[TaskTag]

    def to_str(self) -> str:
        tags = " ".join(f"#{tag}" for tag in self.tags)
        task_prefix = COMPLETED_TASK_PREFIX if self.done else INCOMPLETE_TASK_PREFIX
        if tags:
            task = f"{task_prefix}{self.description}  {tags}"
        else:
            task = f"{task_prefix}{self.description}"

        lines = [
            task,
            *[detail.to_str() for detail in self.details],
        ]

        return "\n".join(lines)


@dataclass
class TaskDetail:
    description: str

    def to_str(self) -> str:
        return f"{DETAIL_PREFIX}{self.description}"


def add_detail_to_task(task: Task, detail: TaskDetail) -> Task:
    new_task = Task(
        description=task.description,
        done=task.done,
        details=[*task.details, detail],
        tags=task.tags,
    )
    return new_task


class EmptyLine:
    def to_str(self) -> str:
        return ""


class ExternalReferencesHeader:
    def to_str(self) -> str:
        return "\n<!-- External references -->\n"


@dataclass
class ExternalReference:
    number: int
    url: str
    description: str

    def to_str(self) -> str:
        return f'[{self.number}]: {self.url} "{self.description}"'


PseudoItem = Union[
    Task,
    TaskDetail,
    EmptyLine,
    ExternalReferencesHeader,
    ExternalReference,
]
Item = Union[Task, ExternalReferencesHeader, ExternalReference]


def parse(raw: MarkdownStr) -> List[Item]:
    # TODO: this function needs a decent refactor
    """
    if line is task, create new task and buffer it
    if next line is detail,
        add detail to previous task,
        remove old task from buffer,
        and store new task in buffer
    if next line is task, flush buffered task, and create new task
    if next line is space, flush buffer, and add space
    """
    parsed_items: List[Item] = []
    buffer: Optional[PseudoItem] = None

    lines = iter(raw.split("\n"))

    for line in lines:
        # identify current line type
        # check buffer
        # decide if to flush buffer or to compose with buffer
        line_is_empty = line == ""
        if line_is_empty:
            empty_line = EmptyLine()
            if not buffer:
                buffer = empty_line
                continue
            else:
                # Flush buffer and add parsed line
                parsed_items.append(cast(Item, buffer))
                if isinstance(buffer, ExternalReferencesHeader):
                    # case: new line after ExternalReferencesHeader
                    # no need to add anything to the buffer
                    buffer = None
                    # TODO: perhaps is best to not to flush this and flush once the
                    # first external reference is found?
                else:
                    buffer = empty_line
                continue

        line_is_task = is_task(line)
        if line_is_task:
            task = parse_task(line)
            if not buffer:
                buffer = task
                continue
            else:
                # Flush buffer and add parsed line
                parsed_items.append(cast(Item, buffer))
                buffer = task
                continue

        line_is_detail = is_detail(line)
        if line_is_detail:
            task_detail = parse_task_detail(line)
            if not buffer:
                raise ValueError("You cannot have details outside a task")
            else:
                # Compose detail with task in buffer
                partially_parsed_task = cast(Task, buffer)
                updated_task = add_detail_to_task(partially_parsed_task, task_detail)
                buffer = updated_task
                continue

        line_is_external_reference_header = is_external_references_header(line)
        if line_is_external_reference_header:
            if not buffer:
                raise ValueError("Empty line expected before external reference header")
            else:
                # Compose header with new line in buffer
                buffer = ExternalReferencesHeader()
                continue

        line_is_external_reference = is_external_reference(line)
        if line_is_external_reference:
            if buffer:
                raise ValueError("Empty line expected before external references")

            external_reference = parse_external_reference(line)
            parsed_items.append(external_reference)
            # TODO: ensure that once you find the first external reference, nothing else
            # can be added to the WIP file
            continue

        raise NotImplementedError(f"Line {line!r} not understood")

    if buffer:
        parsed_items.append(cast(Item, buffer))

    return parsed_items


def is_task(raw_line: MarkdownStr) -> bool:
    task_patterns_in_line = LINE_IS_TASK_PATTERN.match(raw_line)
    _is_task = bool(task_patterns_in_line)
    return _is_task


def is_detail(raw_line: MarkdownStr) -> bool:
    detail_patterns_in_line = LINE_IS_DETAIL_PATTERN.match(raw_line)
    _is_detail = bool(detail_patterns_in_line)
    return _is_detail


def is_external_references_header(raw_line: MarkdownStr) -> bool:
    return raw_line == "<!-- External references -->"


def is_external_reference(raw_line: MarkdownStr) -> bool:
    detail_patterns_in_line = LINE_IS_EXTERNAL_REFERENCE_PATTERN.match(raw_line)
    _is_external_reference = bool(detail_patterns_in_line)
    return _is_external_reference


def parse_task(raw_line: MarkdownStr) -> Task:
    # Remove `- [ ]` prefix to get task description
    if raw_line.startswith(INCOMPLETE_TASK_PREFIX):
        description = raw_line[6:]
        completed = False
    elif raw_line.startswith(COMPLETED_TASK_PREFIX):
        description = raw_line[6:]
        completed = True
    else:
        raise NotImplementedError(
            "OOps, I didn't expect to reach this point. Variables in scope:"
            f"\n{vars()}"
        )

    # Handle task tags
    tags = TASK_TAG_PATTERN.findall(description)

    if tags:
        # Remove tags from description
        for tag in tags:
            description = description.replace(f"#{tag}", "").strip()

    return Task(
        description=description,
        done=completed,
        details=_NO_DETAILS,
        tags=tags,
    )


def parse_task_detail(raw_line: MarkdownStr) -> TaskDetail:
    description = raw_line.replace(DETAIL_PREFIX, "", 1)
    task_detail = TaskDetail(description=description)
    return task_detail


def parse_external_reference(raw_reference: MarkdownStr) -> ExternalReference:
    matches = LINE_IS_EXTERNAL_REFERENCE_PATTERN.match(raw_reference)
    if not matches:
        raise ValueError(
            f"Expected external reference, but {raw_reference!r} found and I cannot"
            " understand it"
        )

    external_reference = ExternalReference(
        number=int(matches.group(1)),
        url=matches.group(2),
        description=matches.group(3),
    )
    return external_reference


def deserialize_content(data: Iterable) -> MarkdownStr:
    lines = [item.to_str() for item in data]
    content = "\n".join(lines)
    return content
