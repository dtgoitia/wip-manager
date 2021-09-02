import json
from pathlib import Path

from src.types import JsonDict, MarkdownStr


def read_markdown_file(path: Path) -> str:
    content = path.read_text()
    return content


def read_json(path: Path) -> JsonDict:
    with path.open("r") as f:
        return json.load(f)


def append_to_archive(*, path: Path, content: MarkdownStr) -> None:
    if not path.exists:
        print(f"{path} does not exist, creating one...")

    with path.open("a") as f:
        f.write(content)
        f.write("\n")  # Ensure there is a new line at the end of the file


def write_text_file(*, path: Path, content: MarkdownStr) -> None:
    path.write_text(content)
