import click

from src.cli.clean import archive_completed_tasks
from src.cli.deadlines import show_tasks_sorted_by_deadline
from src.cli.hash import add_hashes_to_tasks
from src.cli.scrape_tags import dump_tags, print_tags
from src.cli.validate import validate_wip_file
from src.config import get_config


@click.group()
def wip_group():
    ...


@wip_group.command(name="clean", help="Move completed tasks to the archive")
def clean_cmd() -> None:
    config = get_config()
    default_wip_path = config.wip_path
    default_archive_path = config.archive_path
    archive_completed_tasks(path=default_wip_path, archive_path=default_archive_path)


@wip_group.command(name="validate", help="Validate WIP file")
@click.option(
    "--debug",
    is_flag=True,
    default=False,
    help="Dump to compare against the original file",
)
def validate_cmd(debug: bool) -> None:
    config = get_config()
    default_wip_path = config.wip_path
    validate_wip_file(path=default_wip_path, debug=debug)


@wip_group.command(name="hash", help="Add hashes to all tasks without a hash")
def hash_cmd() -> None:
    config = get_config()
    default_wip_path = config.wip_path
    add_hashes_to_tasks(path=default_wip_path)


@wip_group.command(name="deadlines", help="Show tasks sorted by deadline")
def deadlines_cmd() -> None:
    config = get_config()
    default_wip_path = config.wip_path
    show_tasks_sorted_by_deadline(path=default_wip_path)


@wip_group.command(name="tags", help="Print all tag to console")
def tags_cmd() -> None:
    config = get_config()
    paths = [
        config.wip_path,
        config.archive_path,
    ]
    print_tags(paths=paths)


@wip_group.command(name="dump-tags", help="Add WIP and archive tags to config")
def dump_tags_cmd() -> None:
    config = get_config()
    paths = [
        config.wip_path,
        config.archive_path,
    ]
    dump_tags(paths=paths)


if __name__ == "__main__":
    wip_group()
