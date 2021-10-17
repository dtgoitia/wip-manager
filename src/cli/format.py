from pathlib import Path

from src.cli.hash import add_hashes_to_tasks
from src.cli.validate import validate_wip_file
from src.format import add_eof_new_line, tidy_up_external_references


def _pre(message: str) -> None:
    print(f"{message:.<55}", end="")


def _done() -> None:
    print(" done")


def _validate(*, path: Path) -> None:
    _pre("Validating WIP file")
    validate_wip_file(path=path, debug=False)
    _done()


def _add_eof_new_line(*, path: Path) -> None:
    _pre("Adding EOF new line if missing")
    add_eof_new_line(path=path)
    _done()


def _hash(*, path: Path) -> None:
    _pre("Adding hashes to tasks")
    add_hashes_to_tasks(path=path)
    _done()


def _tidy_up_external_references(*, path: Path) -> None:
    _pre("Moving links to external references")
    tidy_up_external_references(path=path)
    _done()


def format(*, path: Path) -> None:
    _validate(path=path)
    _add_eof_new_line(path=path)
    _hash(path=path)
    _tidy_up_external_references(path=path)
