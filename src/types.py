from __future__ import annotations

import re
from dataclasses import dataclass, replace
from typing import Any, Dict, List, Union

MarkdownStr = str
JsonDict = Dict[str, Any]
GroupName = str

INCOMPLETE_TASK_PREFIX = "- [ ] "
COMPLETED_TASK_PREFIX = "- [x] "
DETAIL_PREFIX = "  - "
TASK_TAG_PATTERN = re.compile(r"\s#([a-z]:[a-z0-9-_,]*)")  # `#g:group1_b`
LINE_IS_TASK_PATTERN = re.compile(r"^- \[")  # starts with `- [ ] ` or `- [x] `
LINE_IS_DETAIL_PATTERN = re.compile(r"^  - ")  # starts with `  - `
LINE_IS_EXTERNAL_REFERENCE_PATTERN = re.compile(r'\[([0-9]+)\]: ([^\s]+)\s"(.*)"$')
LINE_IS_TITLE_PATTERN = re.compile(r"^## (.*)$")


@dataclass
class Title:
    title: str

    def to_str(self) -> str:
        return f"## {self.title}"


@dataclass
class Task:
    description: str
    done: bool
    details: List[TaskDetail]
    tags: List[Tag]  # you need to preserve order, no sets

    def add_detail(self, task_detail: TaskDetail) -> Task:
        return replace(self, details=[*self.details, task_detail])

    def to_str(self) -> str:
        tags = " ".join((tag.to_str() for tag in self.tags))
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
class Tag:
    type: str  # g (group), p (priority), etc.
    value: str

    def to_str(self) -> str:
        return f"#{self.type}:{self.value}"


@dataclass
class TaskDetail:
    description: str

    def to_str(self) -> str:
        return f"{DETAIL_PREFIX}{self.description}"


class EmptyLine:
    def to_str(self) -> str:
        return ""

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


class ExternalReferencesHeader:
    def to_str(self) -> str:
        return "<!-- External references -->"


@dataclass
class ExternalReference:
    number: int
    path: str
    description: str

    def to_str(self) -> str:
        return f'[{self.number}]: {self.path} "{self.description}"'


Item = Union[Title, EmptyLine, Task, ExternalReferencesHeader, ExternalReference]
