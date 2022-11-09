import logging

from site_builder.structure_settings import FileSettings


logger = logging.getLogger(__name__)


class FileCollector(list):
    def __init__(self, settings: FileSettings):
        super().__init__()
        self.__source_dir = settings.source_dir
        self.__exclude_files = self.__files_from_pattern(settings.excludes)
        self.__add_files(self.__files_from_pattern(settings.includes))
        self.__add_files(self.__files_from_pattern(settings.uncategorized), warn=True)

    @classmethod
    def from_modified_settings(cls, base_settings: FileSettings, **kwargs):
        base_settings_dict = base_settings.dict()
        base_settings_dict.update(kwargs)
        return cls(FileSettings(**base_settings_dict))

    def __add_files(self, files, warn=False):
        for file in files:
            if file not in self.__exclude_files + self:
                self.append(file)
                if warn:
                    logger.warning(f"Uncategorized file: {file}")

    def __files_from_pattern(self, patterns):
        files = []
        for pattern in patterns:
            if len(new_files := sorted(self.__source_dir.glob(pattern))) > 0:
                files.extend(new_files)
            else:
                logger.warning(f"Can't find any file(s) for: {pattern}")
        return files
