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
        mkdocs_nav = getattr(mkdocs_process.config, "nav", None)

        if mkdocs_nav is None:
            raise ValueError("Error: MkDocs navigation is not initialized. Ensure 'nav:' is defined in mkdocs.yml before running.")

        self.__nav = NavInterface(mkdocs_nav, self.__source_files, self.__name_converter)

    def generate_pages(self):
        mkdocs_process = mkdocs_gen_files.FilesEditor.current()
        mkdocs_files = mkdocs_process.files  

        for source_file in self.__source_files:
            channel_name = self.__name_converter.channel(source_file)
            output_file = source_file.with_suffix('.md')

            self.generate_page(source_file, output_file, channel_name)

            self.__update_nav(source_file.parent, output_file, channel_name)

        # Rebuild navigation after processing all pages
        self.__nav.rebuild_nav(mkdocs_files)

    @staticmethod
    def generate_page(source_file: Path, output_file: Path, channel_name):
        logger.debug(f"📝 Generating page: {output_file}")

        output_file.parent.mkdir(parents=True, exist_ok=True)

        DiscordChannelID.CUR_FILE = output_file

        formatted_channel = f"# {channel_name}\n\n"
        for raw_message in get_raw_messages(source_file.read_text('utf-8')):
            message_formatter = MessageFormatter(raw_message)
            message_formatter.format()
            formatted_channel += str(message_formatter.formatted_message)

        with mkdocs_gen_files.open(output_file, 'w', encoding='utf-8') as file:
            file.write(formatted_channel)

    def __update_nav(self, category_forum_path: Path, output_file, channel_name):
        """Ensures correct Level 2 & 3 nesting in navigation."""
        category, *forum = category_forum_path.parts
        category_name = self.__name_converter.category(category)
        forum_name = self.__name_converter.forum(forum[0]) if forum else None

        corrected_path = output_file.as_posix()

        if corrected_path.startswith("pvme-guides/pvme-guides"):
            corrected_path = corrected_path.replace("pvme-guides/pvme-guides", "pvme-guides", 1)

        self.__nav.add_item(category_name, forum_name, channel_name, corrected_path)
