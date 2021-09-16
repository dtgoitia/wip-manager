from pathlib import Path

from src.cli.hash import add_hashes_to_tasks
from tests.string_comparison import assert_it_has_a_hash


def test_hash_cmd(tmp_path: Path, statics_dir: Path) -> None:
    original_wip_path = statics_dir / "hash_cmd__WIP_original.md"
    expected_wip_path = statics_dir / "hash_cmd__WIP_expected.md"

    # Set up
    wip_path = tmp_path / "WIP.md"
    wip_path.write_text(original_wip_path.read_text())

    # Action
    add_hashes_to_tasks(path=wip_path)

    # Assert
    actual_wip = wip_path.read_text()
    expected_wip = expected_wip_path.read_text()
    # assert actual_wip == expected_wip
    actual_lines = actual_wip.split("\n")
    expected_lines = expected_wip.split("\n")
    for actual_line, expected_line in zip(actual_lines, expected_lines):
        assert_it_has_a_hash(with_hash=expected_line, without_hash=actual_line)
