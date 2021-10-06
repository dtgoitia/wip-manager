import difflib
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

    # Print diff
    original_lines = original_content.split("\n")
    parsed_lines = parsed_content.split("\n")
    differ = difflib.Differ()
    diff = differ.compare(original_lines, parsed_lines)

    diffs_found = False
    for i, line in enumerate(diff):
        if line.startswith("  "):
            continue
        diffs_found = True
        print(i, line)

    if diffs_found:
        # Exiting with error on diff is useful to concatenate CLI instructions
        exit(1)
