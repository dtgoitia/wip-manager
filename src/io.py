import json
import logging
import textwrap
from pathlib import Path

from src.types import JsonDict, MarkdownStr

logger = logging.getLogger(__name__)


def read_markdown_file(path: Path) -> str:
    content = path.read_text()
    return content


def read_json(path: Path) -> JsonDict:
    with path.open("r") as f:
        return json.load(f)


def json_loads_with_trailing_comma(content: str) -> JsonDict:
    # Remove styling: newlines and indentations
    indented_lines = content.split("\n")
    lines_without_indentation = (textwrap.dedent(line) for line in indented_lines)
    without_newlines = "".join(lines_without_indentation)

    # This requires a compact JSON format, without styling
    json_str = without_newlines.replace(",]", "]").replace(",}", "}")

    return json.loads(json_str)


def read_json_with_trailing_comma(path: Path) -> JsonDict:
    content = path.read_text()
    return json_loads_with_trailing_comma(content=content)


def write_json(path: Path, data: JsonDict) -> None:
    with path.open("w") as f:
        return json.dump(data, f, indent=2)


def _add_trailing_comma(line: str) -> str:
    if line.endswith(","):
        return line

    if line.endswith("{"):
        return line

    if line.endswith("["):
        return line

    return f"{line},"


def json_dumps_with_trailing_comma(data: JsonDict) -> str:
    json_str = json.dumps(data, indent=2)

    lines = json_str.split("\n")
    lines_with_trailing_comma = (_add_trailing_comma(line) for line in lines)
    with_trailing_commas = "\n".join(lines_with_trailing_comma)

    # Remove last trailing comma of the file
    json_str_with_trailing_commas = with_trailing_commas[:-1]

    return json_str_with_trailing_commas


def write_json_with_trailing_commas(path: Path, data: JsonDict) -> None:
    json_str = json_dumps_with_trailing_comma(data=data)
    path.write_text(json_str)


def safe_write_json(path: Path, data: JsonDict) -> None:
    original_content = path.read_bytes()

    try:
        write_json_with_trailing_commas(path=path, data=data)
    except TypeError:
        logger.info(f"Error while writing JSON to {path}. Rolling back...")
        path.write_bytes(original_content)

        raise


def append_to_archive(*, path: Path, content: MarkdownStr) -> None:
    if not path.exists:
        print(f"{path} does not exist, creating one...")

    with path.open("a") as f:
        f.write(content)
        f.write("\n")  # Ensure there is a new line at the end of the file


def write_text_file(*, path: Path, content: MarkdownStr) -> None:
    path.write_text(content)
