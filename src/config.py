from dataclasses import dataclass
from pathlib import Path

from src.io import read_json

DEFAULT_CONFIG_PATH = Path("~/.config/wip-manager/config.json").expanduser()


@dataclass
class Config:
    wip_path: Path


def get_config() -> Config:
    content = read_json(path=DEFAULT_CONFIG_PATH)
    return Config(
        wip_path=parse_path(content["wip_path"]),
    )


def parse_path(path_as_str: str) -> Path:
    return Path(path_as_str).expanduser()
