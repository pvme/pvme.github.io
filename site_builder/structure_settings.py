from typing import List, Dict
from pathlib import Path

import yaml
from pydantic import BaseModel


class FileSettings(BaseModel):
    source_dir: Path = Path('pvme-guides')
    includes: List[str] = []
    excludes: List[str] = []
    uncategorized: List[str] = ['**/*.txt']


class NameConvertSettings(BaseModel):
    category: Dict[str, str] = {}
    forum: Dict[str, str] = {}
    word: Dict[str, str] = {}


class StructureSettings(BaseModel):
    files: FileSettings = FileSettings()
    name_convert: NameConvertSettings = NameConvertSettings()

    @classmethod
    def from_yaml(cls, yaml_file):
        with open(yaml_file) as f:
            data = yaml.safe_load(f)
        return cls(**data)
