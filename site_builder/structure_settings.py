from pathlib import Path

import yaml
from pydantic import BaseModel


class FileSettings(BaseModel):
    source_dir: Path = Path('pvme-guides')
    includes: list[str] = []
    excludes: list[str] = []
    # default value to prevent accidentally ignoring guides
    uncategorized: list[str] = ['**/*.txt']


class NavNameSettings(BaseModel):
    alias: str | None = None
    emoji: str | None = None


class NameConvertSettings(BaseModel):
    forum: dict[str, str] = {}
    word: dict[str, str] = {}
    category: dict[str, NavNameSettings] = {}
    # this overrides channel.json
    extra_channel: dict[str, str] = {}


class StructureSettings(BaseModel):
    files: FileSettings = FileSettings()
    name_convert: NameConvertSettings = NameConvertSettings()

    @classmethod
    def from_yaml(cls, yaml_file):
        with open(yaml_file) as f:
            data = yaml.safe_load(f)
        return cls(**data)
