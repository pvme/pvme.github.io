from pathlib import Path
import logging
import shutil
from typing import Union, Tuple, List

import mkdocs_gen_files

# required because mkdocs calls this file dynamically with runpy
import sys
sys.path.append(str(Path.cwd()))
from file_formatter.rules import DiscordChannelID
from file_formatter.message_formatter import RawMessageParser, MessageFormatter


logger = logging.getLogger(__name__)


# contains .txt sources and .md pages under docs/
SOURCE_DIR = Path('pvme-guides')

INCLUDES = [
    'getting-started/quick-start.txt',
    'getting-started/bossing-path.txt',
    'getting-started/revo-to-full-manual.txt',
    'getting-started/interface-guide.txt',
    'getting-started/learning-pvm.txt',

    'invention-and-perks/**/*.txt',
    'miscellaneous-information/**/*.txt',

    'upgrading-info/upgrade-order/*.txt',
    'upgrading-info/**/*.txt',

    'dpm-advice/**/*.txt',
    'afk/**/*.txt',
    'basic-guides/**/*.txt',
    'rs3-full-boss-guides/**/*.txt',

    'slayer/overview-of-slayer.txt',
    'slayer/block-prefer-list.txt',
    'slayer/ultimate-slayer.txt',
    'slayer/miscellaneous-slayer.txt',
    'slayer/**/*.txt',

    'osrs-guides/**/*.txt',
]

EXCLUDES = [
    'archive/**/*.txt',
    'commands/**/*.txt',
    'get-involved/**/*.txt',
    'editor-resources/**/*.txt',
    'navigation/**/*.txt',
    'osrs-commands/**/*.txt',
    'miscellaneous-information/command-info.txt',
    'afk/afk-overview.txt'
]

UNCATEGORIZED = '**/*.txt'


class FileCollector(list):
    def __init__(self, includes, excludes, uncategorized=None, source_dir: Path = SOURCE_DIR):
        super().__init__()
        self.__source_dir = source_dir
        self.__exclude_files = self.__files_from_pattern(excludes)
        self.__add_files(self.__files_from_pattern(includes))
        if uncategorized:
            self.__add_files(self.__files_from_pattern([uncategorized]), warn=True)

    @classmethod
    def from_structure_file(cls, file='structure.ini'):
        pass

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


class Nav(dict):
    def __setitem__(self, keys: Union[str, Tuple[str, ...], List[str]], value: Union[Tuple[str, str], str]):
        # todo: fix type hinting
        if isinstance(keys, str):
            keys = (keys,)

        cur = self
        for key in keys:
            cur = cur.setdefault(key, {})

        cur[value[0]] = value[1]

    @property
    def mkdocs_nav(self):
        return ['index.md'] + [{key: value} for key, value in self.items()]


class PageGenerator:
    def __init__(self, source_files, source_output_dir: Path = SOURCE_DIR):
        self.__source_output_dir = source_output_dir
        self.__source_files = source_files
        self.__custom_channels = {source_output_dir / channel['path']: channel['name'] for channel in
                                  DiscordChannelID.CHANNEL_LOOKUP.values()}
        self.__editor = mkdocs_gen_files.FilesEditor.current()
        self.__nav = Nav()

    def generate_pages(self):
        for source_file in self.__source_files:
            channel_name = self.__custom_channels.get(source_file, source_file.stem).replace('-', ' ').capitalize()
            category_forum = source_file.relative_to(self.__source_output_dir).parent
            output_file = Path(source_file).with_suffix('.md')

            self.generate_page(source_file, output_file, channel_name)
            self.__update_nav(category_forum, output_file, channel_name)

        self.__editor.config.nav = self.__nav.mkdocs_nav

    @staticmethod
    def generate_page(source_file: Path, output_file: Path, channel_name):
        logger.debug(f"formatting: {output_file}")

        # todo: work-around relative links, check if absolute links work
        DiscordChannelID.CUR_FILE = output_file

        text = source_file.read_text('utf-8')

        formatted_channel = f"# {channel_name}\n"
        raw_message_parser = RawMessageParser(text)
        raw_message_parser.parse()
        for raw_message in raw_message_parser.raw_messages:
            message_formatter = MessageFormatter(raw_message)
            message_formatter.format()
            formatted_channel += str(message_formatter.formatted_message)

        with mkdocs_gen_files.open(output_file, 'w', encoding='utf-8') as file:
            file.write(formatted_channel)

    def __update_nav(self, category_forum_path: Path, output_file, channel_name):
        category_forum = [part for part in category_forum_path.parts]
        # category_forum.append(channel_name)
        self.__nav[category_forum] = channel_name, output_file.as_posix()


if __name__ == '__main__':
    # delete previous docs/pvme-guides (section is not called from `mkdocs build`)
    previous_build_dir = Path('docs' / SOURCE_DIR)
    if previous_build_dir.exists():
        shutil.rmtree(previous_build_dir)


logging.basicConfig()
logging.getLogger(__name__).level = logging.DEBUG

files = FileCollector(INCLUDES, EXCLUDES, UNCATEGORIZED)
# files = FileCollector(['upgrading-info/**/*.txt'], EXCLUDES)
page_generator = PageGenerator(files)
page_generator.generate_pages()
