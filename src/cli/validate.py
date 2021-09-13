from pathlib import Path

from src.interpreter import items_to_markdown, parse_document
from src.io import read_markdown_file


def validate_wip_file(*, path: Path, debug: bool) -> None:
    original_content = read_markdown_file(path=path)
    items = parse_document(original_content)
    parsed_content = items_to_markdown(items)

    if debug:
        output_path = path.parent / f"{path.stem}__VALIDATION_DEBUG.md"
        print(f"Parsed content dumped into {output_path}")
        output_path.write_text(parsed_content)

    assert original_content == parsed_content
