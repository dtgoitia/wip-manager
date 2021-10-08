import itertools
from pathlib import Path
from typing import Iterator, List

from src.interpreter import parse_document
from src.io import read_markdown_file
from src.types import GROUP_TAG_TYPE, Tag, Task


def scrape_tags(path: Path) -> Iterator[Tag]:
    original_content = read_markdown_file(path=path)
    items = parse_document(original_content)

    tasks = (item for item in items if isinstance(item, Task))
    tag_lists = (task.tags for task in tasks if task.tags)
    tags = set(tag for tag in itertools.chain.from_iterable(tag_lists))
    yield from tags


def scrape_group_tags(path: Path) -> Iterator[Tag]:
    group_tags = (tag for tag in scrape_tags(path) if tag.type == GROUP_TAG_TYPE)
    yield from group_tags


def print_tags(paths: List[Path]) -> None:
    """Print a sorted list of all groups ('g') tags in WIP and archive."""
    tags_per_file = (scrape_group_tags(path) for path in paths)
    tags = set(tag for tag in itertools.chain.from_iterable(tags_per_file))
    tag_values = (tag.value for tag in tags)
    for tag in sorted(tag_values):
        print(tag)
