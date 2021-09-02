import click

from src.cli.validate import validate_wip_file
from src.config import get_config


@click.group()
def wip_group():
    ...


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


if __name__ == "__main__":
    wip_group()
