import re
from dataclasses import dataclass
from typing import List

MarkdownStr = str
TaskDetail = str
TaskTag = str

INCOMPLETE_TASK_PREFIX = "- [ ] "
COMPLETED_TASK_PREFIX = "- [x] "
DETAIL_PREFIX = "- "
_NO_DETAILS: List[TaskDetail] = []
TASK_TAG_PATTERN = re.compile(r"\s#([a-z]:[a-z0-9-_,]*)\s?")  # `#g:group1_b`
LINE_IS_TASK_PATTERN = re.compile(r"^- \[")  # starts with `- [ ] ` or `- [x] `


@dataclass
class Task:
    description: str
    completed: bool
    details: List[TaskDetail]
    tags: List[TaskTag]


def parse(raw: MarkdownStr) -> List[Task]:
    lines_buffer = []
    parsed_tasks = []

    lines = iter(raw.split("\n"))

    lines_buffer.append(next(lines))
    for line in lines:
        line_is_task = is_task(line)

        if line_is_task:
            # Flush buffered lines
            buffered_lines = "\n".join(lines_buffer)
            task = parse_task(buffered_lines)
            parsed_tasks.append(task)

            # Replace line buffer with current line
            lines_buffer = [line]
        else:
            # At this point you cannot know if the next line is a detail or another task
            lines_buffer.append(line)

    # Flush last bits in the buffer
    buffered_lines = "\n".join(lines_buffer)
    task = parse_task(buffered_lines)
    parsed_tasks.append(task)

    return parsed_tasks


def is_task(raw_line: MarkdownStr) -> bool:
    task_patterns_in_line = LINE_IS_TASK_PATTERN.match(raw_line)
    is_task = bool(task_patterns_in_line)
    return is_task


def parse_task(raw: MarkdownStr) -> Task:
    task_has_details = "\n" in raw
    if task_has_details:
        description, raw_details = raw.split("\n", maxsplit=1)
        details = parse_details(raw_details)
    else:
        description = raw
        details = _NO_DETAILS

    # Get task description - aka: remove `- [ ]` prefix and appended tags
    completed = False

    if description.startswith(INCOMPLETE_TASK_PREFIX):
        description = description[6:]
    elif description.startswith(COMPLETED_TASK_PREFIX):
        description = description[6:]
        completed = True
    else:
        raise NotImplementedError(
            "OOps, I didn't expect to reach this point. Variables in scope:"
            f"\n{vars()}"
        )

    tags = TASK_TAG_PATTERN.findall(description)

    if tags:
        # Remove tags from description
        for tag in tags:
            description = description.replace(f"#{tag}", "").strip()

    return Task(
        description=description,
        completed=completed,
        details=details,
        tags=tags,
    )


def parse_details(raw_details: MarkdownStr) -> List[TaskDetail]:
    lines = (line.strip() for line in raw_details.strip().split("\n"))
    raw_per_detail = (line for line in lines if line.startswith(DETAIL_PREFIX))
    details = [raw_detail.replace(DETAIL_PREFIX, "") for raw_detail in raw_per_detail]
    return details
