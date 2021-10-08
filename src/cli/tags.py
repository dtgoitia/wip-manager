import dataclasses
import itertools
from pathlib import Path
from typing import Iterator, List

from src.config import get_config, update_config
from src.interpreter import parse_document
from src.io import read_markdown_file
from src.types import GROUP_TAG_TYPE, Tag, TagValue, Task


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


def get_all_group_tags(paths: List[Path]) -> Iterator[TagValue]:
    """Return group tag values in config and in WIP and archive files."""
    tags_per_file = (scrape_group_tags(path) for path in paths)
    tags_in_files = set(tag for tag in itertools.chain.from_iterable(tags_per_file))

    config = get_config()
    tags_in_config = set((Tag(type=GROUP_TAG_TYPE, value=v) for v in config.tags))

    tags = tags_in_config.union(tags_in_files)

    tag_values = (tag.value for tag in tags)
    return tag_values


def print_tags(paths: List[Path]) -> None:
    """Print all groups tags to console."""
    tag_values = get_all_group_tags(paths=paths)
    for tag in sorted(tag_values):
        print(tag)


def dump_group_tags(paths: List[Path]) -> None:
    """Add group tags in WIP and archive files to config."""
    tag_values = get_all_group_tags(paths=paths)
    sorted_tag_values = list(sorted(tag_values))

    config = get_config()
    updated_config = dataclasses.replace(config, tags=sorted_tag_values)

    update_config(config=updated_config)
