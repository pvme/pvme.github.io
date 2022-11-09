from typing import List
from pathlib import Path

import yaml
from pydantic import BaseModel


class FileSettings(BaseModel):
    source_dir: Path = Path('pvme-guides')
    includes: List[str] = []
    excludes: List[str] = []
    uncategorized: List[str] = ['**/*.txt']


class StructureSettings(BaseModel):
    files: FileSettings = FileSettings()

    @classmethod
    def from_yaml(cls, yaml_file):
        with open(yaml_file) as f:
            data = yaml.safe_load(f)
        return cls(**data)
