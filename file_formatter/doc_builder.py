"""Process of reading guide.txt files and writing the formatted guide.md files to the docs folder
"""
import os
import shutil
import logging

import ruamel.yaml

from file_formatter.rules import DiscordChannelID
from file_formatter.message_formatter import RawMessageParser, MessageFormatter

logger = logging.getLogger('file_formatter.file_writer')
logger.level = logging.WARN

CATEGORY_SEQUENCE = [
    'getting-started',
    'miscellaneous-information',
    'upgrading-info',
    'dpm-advice',
    'basic-guides',
    'low-tier-pvm',
    'mid-tier-pvm',
    'high-tier-pvm',
    'angel-of-death',
    'heart-of-gielinor',
    'elder-god-wars',
    'elite-dungeons',
    'nex',
    'slayer',
    'solak',
    'telos',
    'vorago',
    'zamorak'
]


def generate_channel_source(channel_txt_file, source_dir, category_name, channel_name):
    # read guide.txt
    with open(channel_txt_file, 'r', encoding='utf-8') as file:
        text = file.read()

    # set channel title
    formatted_channel = '# {}\n'.format(channel_name.replace('-', ' ').capitalize())

    # parse and format messages
    raw_message_parser = RawMessageParser(text)
    raw_message_parser.parse()

    for raw_message in raw_message_parser.raw_messages:
        message_formatter = MessageFormatter(raw_message)
        message_formatter.format()
        formatted_channel += str(message_formatter.formatted_message)

    # write the formatted channel data to guide.md
    with open('{}/pvme-guides/{}/{}.md'.format(source_dir, category_name, channel_name), 'w', encoding='utf-8') as file:
        file.write(formatted_channel)


def update_mkdocs_nav(mkdocs_yml: str, mkdocs_nav: list):
    with open(mkdocs_yml, 'r') as file:
        raw_text = file.read()

    yaml = ruamel.yaml.YAML()
    data = yaml.load(raw_text)

    mkdocs_nav.insert(0, 'index.md')
    data['nav'] = mkdocs_nav

    with open(mkdocs_yml, 'w') as file:
        yaml.dump(data, file)


def generate_sources(pvme_guides_dir: str, source_dir: str, mkdocs_yml: str) -> int:
    # (clear) + create the source/pvme-guides directory (only really needed for debugging)
    if os.path.isdir('{}/pvme-guides'.format(source_dir)):
        shutil.rmtree('{}/pvme-guides'.format(source_dir), ignore_errors=True)

    os.mkdir('{}/pvme-guides'.format(source_dir))

    channel_map = {channel['path']: channel['name'] for channel in DiscordChannelID.CHANNEL_LOOKUP.values()}

    mkdocs_nav = list()     # contents of the mkdocs.yml nav:

    # only search for categories in category sequence, automatically excludes unused categories
    for category_name in CATEGORY_SEQUENCE:
        category_dir = '{}/{}'.format(pvme_guides_dir, category_name)

        # exclude non-directories like README.md and LICENSE
        if not os.path.isdir(category_dir):
            continue

        os.mkdir('{}/pvme-guides/{}'.format(source_dir, category_name))

        # convert high-tier-pvm > High tier pvm
        formatted_category = category_name.replace('-', ' ').capitalize()
        category_channels = list()

        # iterate channels (dpm-advice.dpm-advice-faq.txt etc)
        for channel_file in sorted(os.listdir(category_dir)):
            channel_dir = '{}/{}'.format(category_dir, channel_file)
            channel_name, ext = os.path.splitext(channel_file)

            if ext != '.txt':
                continue

            channel_path = f'{category_name}/{channel_name}{ext}'
            discord_name = channel_map[channel_path] if channel_path in channel_map else channel_name
            logger.debug(f"formatting {category_name}/{discord_name}.md")
            generate_channel_source(channel_dir, source_dir, category_name, discord_name)

            category_channels.append('pvme-guides/{}/{}.md'.format(category_name, discord_name))

        mkdocs_nav.append({formatted_category: sorted(category_channels)})

    update_mkdocs_nav(mkdocs_yml, mkdocs_nav)

    return 0


if __name__ == '__main__':
    # for debugging
    logging.basicConfig()
    logging.getLogger('file_formatter.file_writer').level = logging.DEBUG
    logging.getLogger('file_formatter.rules_new').level = logging.DEBUG
    logging.getLogger('file_formatter.util').level = logging.DEBUG

    generate_sources('../pvme-guides', '../docs', '../mkdocs.yml')
