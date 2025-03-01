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
        # Strip 'pvme-guides' from the path to get the actual category
        path_parts = category_forum_path.parts[1:]  # Skip the 'pvme-guides' part
        category_name = path_parts[0].lower()  # This should be the category like 'afk'
        forum_name = path_parts[1].lower() if len(path_parts) > 1 else None  # Get the forum if it exists

        corrected_path = output_file.as_posix()

        # Access the navigation structure
        nav_structure = self.__nav.get_nav_structure()

        # Keep a reference to the original structure
        original_nav_structure = self.__store_original_nav_structure(nav_structure)

        # Preprocess nav structure to trim paths before "/" and remove ".md"
        self.__preprocess_nav_structure(nav_structure)

        # logger.debug(f"🔍 Preprocessed nav structure: {nav_structure}")

        # Iterate over the nav structure and look for the correct category and subcategory
        for section in nav_structure:
            if isinstance(section, dict):
                for section_name, subcategories in section.items():
                    # Log each section and its subcategories for inspection
                    # logger.debug(f"📂 Inspecting section: {section_name} with subcategories: {subcategories}")

                    # Check if the category matches
                    if category_name in [item.lower() if isinstance(item, str) else item.lower() for sub_category in subcategories for item in (sub_category.values() if isinstance(sub_category, dict) else [sub_category])]:
                        logger.debug(f"✅ Found category: {category_name}")

                        # Iterate through subcategories in this section (level 2)
                        if isinstance(subcategories, list):
                            for sub_category in subcategories:
                                if isinstance(sub_category, dict):
                                    for sub_category_name, sub_category_path in sub_category.items():
                                        # Normalize subcategory name and path
                                        sub_category_path_normalized = sub_category_path.lower().replace(" ", "-")

                                        # Check if the path matches
                                        if sub_category_path_normalized == category_name:
                                            # Retrieve the original section name from the stored reference
                                            original_section_name = original_nav_structure[section_name]
                                            
                                            # Add the page to this subcategory using the original structure
                                            original_section_name.append({channel_name: corrected_path})
                                            logger.debug(f"📌 Added page under subcategory: '{sub_category_name}'")
                                            return
                                        else:
                                            logger.warning(f"⚠️ Subcategory '{forum_name}' not found in '{category_name}'")
                                elif isinstance(sub_category, str):  # Handle case when sub_category is just a string (without being inside a dictionary)
                                    if sub_category.lower() == category_name:
                                        # Directly add to subcategory
                                        sub_category.append({channel_name: corrected_path})
                                        logger.debug(f"📌 Added page under subcategory: '{sub_category}'")
                                        return

                        else:
                            logger.warning(f"⚠️ Subcategories for '{category_name}' are not in the expected format.")

        # If no matching category was found
        logger.warning(f"⚠️ No matching category found for '{category_name}' in the nav structure.")

    def __store_original_nav_structure(self, nav_structure):
        """Store the original structure for later reference."""
        original_structure = {}
        for section in nav_structure:
            if isinstance(section, dict):
                for section_name, subcategories in section.items():
                    # Store original section names
                    original_structure[section_name] = subcategories
        return original_structure

    def __preprocess_nav_structure(self, nav_structure):
        """Preprocess nav structure to trim paths and remove extensions"""
        for section in nav_structure:
            if isinstance(section, dict):
                for section_name, subcategories in section.items():
                    # If section has subcategories (nested dictionaries)
                    if isinstance(subcategories, list):
                        for sub_category in subcategories:
                            for sub_category_name, sub_category_path in sub_category.items():
                                # If path contains "/", remove everything before it and also remove ".md"
                                sub_category_path = sub_category_path.split('/')[1] if '/' in sub_category_path else sub_category_path
                                sub_category_path = sub_category_path.replace(".md", "").lower()

                                # Update subcategory path
                                sub_category[sub_category_name] = sub_category_path

