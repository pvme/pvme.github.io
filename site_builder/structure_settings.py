from typing import List, Dict, Optional
from pathlib import Path

import yaml
from pydantic import BaseModel


class FileSettings(BaseModel):
    source_dir: Path = Path('pvme-guides')
    includes: List[str] = []
    excludes: List[str] = []
    # default value to prevent accidentally ignoring guides
    uncategorized: List[str] = ['**/*.txt']


class NavNameSettings(BaseModel):
    alias: Optional[str]
    emoji: Optional[str]


class NameConvertSettings(BaseModel):
    forum: Dict[str, str] = {}
    word: Dict[str, str] = {}
    category: Dict[str, NavNameSettings] = {}


class StructureSettings(BaseModel):
    files: FileSettings = FileSettings()
    name_convert: NameConvertSettings = NameConvertSettings()

    @classmethod
    def from_yaml(cls, yaml_file):
        with open(yaml_file) as f:
            data = yaml.safe_load(f)
        return cls(**data)
