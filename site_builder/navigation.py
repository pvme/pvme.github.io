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

    def get_nav_structure(self):
        """Returns the internal navigation structure."""
        return self.__nav

    def add_item(self, category_name: str, forum_name: str, channel_name: str, output_file: str):
        """Ensures Level 2 appears first, then nests Level 3 pages under it properly."""
        if forum_name:
            self.__structure[category_name][forum_name].append({channel_name: output_file})
        else:
            self.__structure[category_name][channel_name] = output_file

    def rebuild_nav(self, mkdocs_files):
        """Ensures that sub-pages are correctly collected and nested under their respective sections."""
        logger.debug("🔍 Rebuilding MkDocs Navigation")

        nav = []

        # Force all paths to use forward slashes to avoid Windows path issues
        all_md_files = [
            Path(file.src_path).as_posix() for file in mkdocs_files if Path(file.src_path).suffix == ".md"
        ]
        logger.debug(f"📄 ALL MkDocs Markdown Files: {all_md_files}")

        # Iterate through all sections in HARDCODED_NAV
        for section in HARDCODED_NAV:
            if isinstance(section, dict):
                # Look for the "Boss & Slayer Guides" section and process it
                if "Boss & Slayer Guides" in section:
                    category_entries = section["Boss & Slayer Guides"]
                    logger.debug(f"📂 Found Boss & Slayer Guides Categories: {category_entries}")

                    boss_guides_section = {"Boss & Slayer Guides": []}

                    for entry in category_entries:
                        if isinstance(entry, dict):
                            for category, folder in entry.items():
                                # Convert section name to lowercase and replace spaces with hyphens for folder path
                                category_folder = category.lower().replace(" ", "-")

                                # Find all markdown files for this category and subfolders (excluding 'index.md' for redirects)
                                category_guides = sorted(
                                    [file for file in all_md_files if f"pvme-guides/{category_folder}/" in file and "index.md" not in file]
                                )

                                # Check if category guides are found, if so, add them
                                if category_guides:
                                    boss_guides_section["Boss & Slayer Guides"].append({category: category_guides})
                                    logger.debug(f"📌 Added {len(category_guides)} guides under '{category}'.")
                                else:
                                    # Ensure empty categories still appear as placeholders
                                    boss_guides_section["Boss & Slayer Guides"].append({category: folder})
                                    logger.warning(f"⚠️ No guides found for '{category}', keeping as placeholder.")

                    # Add the Boss & Slayer Guides section to the nav
                    nav.append(boss_guides_section)

                # For all other sections (excluding "Boss & Slayer Guides"), just add them to the nav
                else:
                    nav.append(section)

        # Rebuild the final nav structure, preserving the order defined in mkdocs.yml
        self.__nav.clear()
        self.__nav.extend(nav)
        logger.debug(f"✅ Final Navigation Structure:\n{self.__nav}")
