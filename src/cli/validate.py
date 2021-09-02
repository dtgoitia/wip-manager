from pathlib import Path

from src.io import read_markdown_file
from src.types import deserialize_content, parse_items


def validate_wip_file(*, path: Path, debug: bool) -> None:
    original_content = read_markdown_file(path=path)
    items = parse_items(original_content)
    parsed_content = deserialize_content(items)

    if debug:
        output_path = path.parent / "WIP_TODO_parsed.md"
        print(f"Parsed content dumped into {output_path}")
        output_path.write_text(parsed_content)

    assert original_content == parsed_content
