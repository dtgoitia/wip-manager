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


@dataclass
class Task:
    description: str
    completed: bool
    details: List[TaskDetail]
    tags: List[TaskTag]


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
