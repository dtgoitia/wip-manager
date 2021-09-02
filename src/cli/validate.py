from pathlib import Path

from src.io import read_markdown_file
from src.types import deserialize_content, parse


def validate_wip_file(path: Path) -> None:
    original_content = read_markdown_file(path=path)
    items = parse(original_content)
    parsed_content = deserialize_content(items)
    assert original_content == parsed_content
