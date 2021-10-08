import dataclasses
import itertools
from pathlib import Path
from typing import Iterator, List

from src.config import get_config, update_config
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


def dump_tags(paths: List[Path]) -> None:
    """Add tags in WIP and archive files to config."""
    tags_per_file = (scrape_group_tags(path) for path in paths)
    tags_in_files = set(tag for tag in itertools.chain.from_iterable(tags_per_file))

    config = get_config()
    tags_in_config = set((Tag(type=GROUP_TAG_TYPE, value=v) for v in config.tags))

    tags = tags_in_config.union(tags_in_files)

    tag_values = (tag.value for tag in tags)
    sorted_tag_values = list(sorted(tag_values))

    updated_config = dataclasses.replace(config, tags=sorted_tag_values)
    update_config(config=updated_config)
