import json
from pathlib import Path

from src.types import JsonDict


def read_markdown_file(path: Path) -> str:
    content = path.read_text()
    return content


def read_json(path: Path) -> JsonDict:
    with path.open("r") as f:
        return json.load(f)
