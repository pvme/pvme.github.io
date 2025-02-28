import yaml
import logging
from typing import List
from pathlib import Path
from collections import defaultdict

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Load NAV structure from mkdocs.yml
def load_nav_from_mkdocs():
    mkdocs_path = Path("mkdocs.yml")
    with mkdocs_path.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file)
        return config.get("nav", [])

HARDCODED_NAV = load_nav_from_mkdocs()

class NavInterface:
    def __init__(self, mkdocs_nav, source_files, name_converter):
        if mkdocs_nav is None:
            raise ValueError("Error: MkDocs navigation is None. Ensure 'nav:' is properly initialized.")

        self.__nav = mkdocs_nav
        self.__source_files = source_files
        self.__name_converter = name_converter
        self.__structure = defaultdict(lambda: defaultdict(list))

    def add_item(self, category_name: str, forum_name: str, channel_name: str, output_file: str):
        """Ensures Level 2 appears first, then nests Level 3 pages under it properly."""
        if forum_name:
            self.__structure[category_name][forum_name].append({channel_name: output_file})
        else:
            self.__structure[category_name][channel_name] = output_file

    def find_first_guide(self, category_folder, mkdocs_files):
        """Finds the first available markdown file inside a given category."""
        logger.debug(f"🔍 Searching for guides in category: {category_folder}")

        # Normalize category path for comparison
        expected_prefix = f"pvme-guides/{category_folder}/"

        # Retrieve and sort relevant markdown files
        md_files = sorted(
            [file.src_path for file in mkdocs_files if file.src_path.startswith(expected_prefix) and file.src_path.endswith(".md")]
        )

        logger.debug(f"📄 Found {len(md_files)} markdown files for {category_folder}: {md_files}")

        return md_files[0] if md_files else None  # Return first guide if found

    def rebuild_nav(self, mkdocs_files):
        """Ensures 'Boss Guides' appears with its subcategories and actual guides."""
        logger.debug("🔍 Rebuilding MkDocs Navigation")

        nav = []

        # Force all paths to use forward slashes to avoid Windows path issues
        all_md_files = [file.src_path.replace("\\", "/") for file in mkdocs_files if file.src_path.endswith(".md")]
        logger.debug(f"📄 ALL MkDocs Markdown Files: {all_md_files}")

        # Load Boss Guides categories from HARDCODED_NAV
        boss_guides_section = None
        for section in HARDCODED_NAV:
            if isinstance(section, dict) and "Boss Guides" in section:
                category_entries = section["Boss Guides"]
                logger.debug(f"📂 Found Boss Guides Categories: {category_entries}")

                # Initialize Boss Guides with its landing page
                boss_guides_section = {"Boss Guides": []}

                for entry in category_entries:
                    if isinstance(entry, dict):
                        for category, folder in entry.items():
                            # Find all markdown files within the category (recursive scan)
                            category_guides = sorted(
                                [file for file in all_md_files if file.startswith(f"pvme-guides/{folder}/")]
                            )

                            if category_guides:
                                # Append actual guides under each category
                                boss_guides_section["Boss Guides"].append({category: category_guides})
                                logger.debug(f"📌 Added {len(category_guides)} guides under '{category}'.")
                            else:
                                # Ensure empty categories still exist as placeholders
                                boss_guides_section["Boss Guides"].append({category: folder})
                                logger.warning(f"⚠️ No guides found for '{category}', keeping as placeholder.")

                    elif isinstance(entry, str):
                        # Ensure the landing page is added first
                        boss_guides_section["Boss Guides"].insert(0, entry)
                        logger.debug(f"📌 Added Boss Guides Landing Page: {entry}")

                break  # We only need to process Boss Guides once

        if boss_guides_section:
            nav.append(boss_guides_section)
        else:
            logger.warning("⚠️ Boss Guides structure not found, skipping.")

        # Preserve other sections
        for section in HARDCODED_NAV:
            if isinstance(section, dict) and "Boss Guides" not in section:
                nav.append(section)

        self.__nav.clear()
        self.__nav.extend(nav)
        logger.debug(f"✅ Final Navigation Structure:\n{self.__nav}")
