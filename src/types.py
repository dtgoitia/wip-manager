from dataclasses import dataclass
from typing import List

MarkdownStr = str
TaskDetail = str

INCOMPLETE_TASK_PREFIX = "- [ ] "
COMPLETED_TASK_PREFIX = "- [x] "
DETAIL_PREFIX = "- "
_NO_DETAILS: List[TaskDetail] = []


@dataclass
class Task:
    description: str
    completed: bool
    details: List[TaskDetail]


def parse(raw: MarkdownStr) -> Task:
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

    if description.startswith(COMPLETED_TASK_PREFIX):
        description = description[6:]
        completed = True

    return Task(description=description, completed=completed, details=details)


def parse_details(raw: MarkdownStr) -> List[TaskDetail]:
    lines = (line.strip() for line in raw.strip().split("\n"))
    raw_details = (line for line in lines if line.startswith(DETAIL_PREFIX))
    details = [raw_detail.replace(DETAIL_PREFIX, "") for raw_detail in raw_details]
    return details
