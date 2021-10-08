from dataclasses import dataclass
from pathlib import Path
from typing import List

from src.io import read_json_with_trailing_comma, safe_write_json
from src.types import JsonDict, TagValue

DEFAULT_CONFIG_PATH = Path("~/.config/wip-manager/config.json").expanduser()


@dataclass
class Config:
    wip_path: Path
    archive_path: Path
    tags: List[TagValue]

    def to_json(self) -> JsonDict:
        json_dict = dict(
            wip_path=str(self.wip_path),
            archive_path=str(self.archive_path),
            tags=sorted(self.tags),
        )
        assert json_dict.keys() == self.__dict__.keys()
        return json_dict


def get_config() -> Config:
    content = read_json_with_trailing_comma(path=DEFAULT_CONFIG_PATH)
    config = Config(
        wip_path=parse_path(content["wip_path"]),
        archive_path=parse_path(content["archive_path"]),
        # if no "tags" in config, add them
        tags=list(sorted(content.get("tags", []))),
    )
    return config


def parse_path(path_as_str: str) -> Path:
    return Path(path_as_str).expanduser()


def update_config(config: Config) -> None:
    assert isinstance(config, Config)
    safe_write_json(path=DEFAULT_CONFIG_PATH, data=config.to_json())
