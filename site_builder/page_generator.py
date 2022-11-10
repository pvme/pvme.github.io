import logging
from typing import List
from pathlib import Path

import mkdocs_gen_files

from site_builder.navigation import NavInterface
from site_builder.formatter.rules import DiscordChannelID
from site_builder.raw_message_parser import get_raw_messages
from site_builder.formatter.message_formatter import MessageFormatter
from site_builder.name_conversion import NameConverter


logger = logging.getLogger(__name__)


class PageGenerator:
    def __init__(self, source_files: List[Path], name_converter: NameConverter, source_output_dir: Path):
        self.__source_output_dir = source_output_dir
        self.__source_files = source_files
        self.__name_converter = name_converter

        mkdocs_process = mkdocs_gen_files.FilesEditor.current()
        self.__nav = NavInterface(mkdocs_process.config.nav)

    def generate_pages(self):
        for source_file in self.__source_files:
            channel_name = self.__name_converter.channel(source_file)
            output_file = source_file.with_suffix('.md')

            self.generate_page(source_file, output_file, channel_name)
            self.__update_nav(source_file.relative_to(self.__source_output_dir).parent, output_file, channel_name)

        self.__nav.update_mkdocs_nav()

    @staticmethod
    def generate_page(source_file: Path, output_file: Path, channel_name):
        logger.debug(f"formatting: {output_file}")

        # todo: work-around relative links, check if absolute links work
        DiscordChannelID.CUR_FILE = output_file

        formatted_channel = f"# {channel_name}\n"
        for raw_message in get_raw_messages(source_file.read_text('utf-8')):
            message_formatter = MessageFormatter(raw_message)
            message_formatter.format()
            formatted_channel += str(message_formatter.formatted_message)

        with mkdocs_gen_files.open(output_file, 'w', encoding='utf-8') as file:
            file.write(formatted_channel)

    def __update_nav(self, category_forum_path: Path, output_file, channel_name):
        category, *forum = category_forum_path.parts
        category_name = self.__name_converter.category(category)
        forum_name = self.__name_converter.forum(forum[0]) if len(forum) > 0 else None

        self.__nav.add_item(category_name, forum_name, channel_name, output_file.as_posix())