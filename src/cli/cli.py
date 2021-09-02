import click

from src.cli.validate import validate_wip_file
from src.config import get_config


@click.group()
def wip_group():
    ...


@wip_group.command(name="validate", help="Validate WIP file")
def validate_cmd() -> None:
    config = get_config()
    default_wip_path = config.wip_path
    validate_wip_file(path=default_wip_path)


if __name__ == "__main__":
    wip_group()
