from pathlib import Path
import logging
import shutil

import sys
sys.path.append(str(Path.cwd()))
from site_builder.structure_settings import StructureSettings
from site_builder.file_collector import FileCollector
from site_builder.page_generator import PageGenerator


logging.basicConfig()
logging.getLogger('site_builder.page_generator').level = logging.DEBUG


if __name__ == '__main__':
    if (previous_build_dir := Path('docs/pvme-guides')).exists():
        shutil.rmtree(previous_build_dir)

settings = StructureSettings.from_yaml('structure_settings.yml')

# uncomment for live-build
files = FileCollector(settings.files)

# uncomment for debugging
# files = FileCollector.from_modified_settings(settings.files, includes=['upgrading-info/**/*.txt'], uncategorized=[])

page_generator = PageGenerator(files, settings.files.source_dir)
page_generator.generate_pages()
