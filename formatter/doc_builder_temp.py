"""Process of reading guide.txt files and writing the formatted guide.md files to the docs folder
"""
import os
import shutil
import logging

import ruamel.yaml

from formatter.rules import DiscordChannelID
from formatter.message_formatter import RawMessageParser, MessageFormatter

logger = logging.getLogger('formatter.file_writer')
logger.level = logging.WARN

CATEGORY_SEQUENCE = [
    'getting-started',
    'miscellaneous-information',
    'afk'
    {'upgrading-info': [
        'upgrade-order'
    ]},
    'dpm-advice',
    'basic-guides',
    {'elder-god-wars': [
        'zamorak'
    ]},
    'elite-dungeons',
    'low-tier-pvm',
    {'mid-tier-pvm': [
        'nex'
    ]},
    {'high-tier-pvm': [
        'angel-of-death',
        'araxxor',
        'raksha',
        'solak',
        'telos',
        'vorago',
    ]},
    'slayer',
    'heart-of-gielinor',
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


def generate_category(pvme_guides_dir: str, source_dir: str, category: str) -> list:
    category_dir = '{}/{}'.format(pvme_guides_dir, category)

    os.mkdir('{}/pvme-guides/{}'.format(source_dir, category))

    channels = list()

    # iterate channels (dpm-advice.dpm-advice-faq.txt etc)
    for channel_file in sorted(os.listdir(category_dir)):
        channel_dir = '{}/{}'.format(category_dir, channel_file)
        channel_name, ext = os.path.splitext(channel_file)

        if ext != '.txt':
            continue

        logger.debug(f"formatting {category}/{channel_name}.md")
        generate_channel_source(channel_dir, source_dir, category, channel_name)

        channels.append('pvme-guides/{}/{}.md'.format(category, channel_name))

    return channels


def format_category_name(category: str) -> str:
    return category.replace('-', ' ').capitalize()


def generate_sources(pvme_guides_dir: str, source_dir: str, mkdocs_yml: str) -> int:
    # (clear) + create the source/pvme-guides directory (only really needed for debugging)
    if os.path.isdir('{}/pvme-guides'.format(source_dir)):
        shutil.rmtree('{}/pvme-guides'.format(source_dir), ignore_errors=True)

    # create base output folder
    os.mkdir('{}/pvme-guides'.format(source_dir))

    # todo: unused until github structure is finalized
    # channel_map = {channel['path']: channel['name'] for channel in DiscordChannelID.CHANNEL_LOOKUP.values()}

    mkdocs_nav = list()  # contents of the mkdocs.yml nav:

    for category in CATEGORY_SEQUENCE:
        if isinstance(category, dict):
            main_category = list(category.keys())[0]
            main_category_channels = generate_category(pvme_guides_dir, source_dir, main_category)
            category_nav = list()

            for sub_category in category[main_category]:
                channels = generate_category(pvme_guides_dir, source_dir, f"{main_category}/{sub_category}")
                category_nav.append({format_category_name(sub_category): channels})

            category_nav.extend(sorted(main_category_channels))
            mkdocs_nav.append({format_category_name(main_category): category_nav})
        else:
            channels = generate_category(pvme_guides_dir, source_dir, category)
            mkdocs_nav.append({format_category_name(category): sorted(channels)})

    update_mkdocs_nav(mkdocs_yml, mkdocs_nav)

    return 0


if __name__ == '__main__':
    # for debugging
    logging.basicConfig()
    logging.getLogger('formatter.file_writer').level = logging.DEBUG
    logging.getLogger('formatter.rules_new').level = logging.DEBUG
    logging.getLogger('formatter.util').level = logging.DEBUG

    generate_sources('../pvme-guides', '../docs', '../mkdocs.yml')
