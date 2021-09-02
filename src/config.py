from dataclasses import dataclass
from pathlib import Path

from src.io import read_json

DEFAULT_CONFIG_PATH = Path("~/.config/wip-manager/config.json").expanduser()


@dataclass
class Config:
    wip_path: Path
    completed_path: Path


def get_config() -> Config:
    content = read_json(path=DEFAULT_CONFIG_PATH)
    config = Config(
        wip_path=parse_path(content["wip_path"]),
        completed_path=parse_path(content["completed_path"]),
    )
    return config


def parse_path(path_as_str: str) -> Path:
    return Path(path_as_str).expanduser()
