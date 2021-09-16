from pathlib import Path

from src.cli.clean import archive_completed_tasks


def test_clean_cmd(tmp_path: Path, statics_dir: Path) -> None:
    original_wip_path = statics_dir / "clean_cmd__WIP_original.md"
    expected_wip_path = statics_dir / "clean_cmd__WIP_expected.md"
    original_archive_path = statics_dir / "clean_cmd__archive_original.md"
    expected_archive_path = statics_dir / "clean_cmd__archive_expected.md"

    # Set up
    wip_path = tmp_path / "WIP.md"
    wip_path.write_text(original_wip_path.read_text())
    archive_path = tmp_path / "archive.md"
    archive_path.write_text(original_archive_path.read_text())

    # Action
    archive_completed_tasks(path=wip_path, archive_path=archive_path)

    # Assert
    actual_wip = wip_path.read_text()
    expected_wip = expected_wip_path.read_text()
    assert actual_wip == expected_wip

    actual_archive = archive_path.read_text()
    expected_archive = expected_archive_path.read_text()
    assert actual_archive == expected_archive
