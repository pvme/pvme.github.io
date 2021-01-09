"""
Mkdocs specific formatting that is based on the standard Mkdocs structure.
Short overview of formatting:

1. iterate the categories and channels in CATEGORY_SEQUENCE
2. format the channels and write them to the docs folder:
    1. parse messages
    2. format messages
    3. format channels
3. overwrite the mkdocs.yml nav: section
"""
import os
import shutil
import logging

import ruamel.yaml

from formatter.rules import *


logger = logging.getLogger('formatter.mkdocs')
logger.level = logging.WARN

CATEGORY_SEQUENCE = [
    'information',
    'getting-started',
    'upgrading-info',
    'miscellaneous-information',
    'dpm-advice',
    'low-tier-pvm',
    'mid-tier-pvm',
    'high-tier-pvm',
    'slayer'
]

DEFAULT_FORMAT_SEQUENCE = [
    Section,
    LineBreak,
    EmbedLink,
    Emoji,
    Insert,
    DiscordWhiteSpace,
    CodeBlock,
    PVMESpreadSheet,
    DiscordChannelID,
    DiscordUserID,
    DiscordRoleID
]


class MKDocsMessage(object):
    def __init__(self, content, embeds, bot_command):
        self.content = content
        self.embeds = embeds if embeds else list()
        self.bot_command = bot_command

    @classmethod
    def init_raw_message(cls, raw_content, raw_bot_command):
        return cls(raw_content, None, raw_bot_command)

    def format_bot_command(self):
        PVMEBotCommand.format_mkdocs_md(self)

    def format_content(self, format_sequence: list = None):
        format_sequence = format_sequence if format_sequence else DEFAULT_FORMAT_SEQUENCE

        for formatter in format_sequence:
            formatter.format_mkdocs_md(self)

    def __str__(self):
        # todo: remove unnecessary spaces (won't affect html report but it's a bit cleaner)
        bot_command_spacing = '\n' if self.bot_command != '' else ''
        return '{}\n{}\n{}{}\n'.format(
            '\n\n'.join(self.content.splitlines()),
            '\n\n'.join(self.embeds),
            bot_command_spacing,
            self.bot_command)


def generate_channel_source(channel_txt_file, source_dir, category_name, channel_name):
    with open(channel_txt_file, 'r', encoding='utf-8') as file:
        raw_data = file.read()

    # obtain all the messages using the . separator
    messages = list()
    message_lines = list()
    for line in raw_data.splitlines():
        if line.startswith('.'):
            messages.append(MKDocsMessage.init_raw_message("\n".join(message_lines), line))
            message_lines = list()
        elif line.startswith('> ') and 'table of contents' in line.lower():
            break
        elif category_name == 'getting-started' and channel_name == 'perks' and line == '__**Table of Contents**__':
            # todo: remove edge-case when the .txt file is updated
            break
        else:
            message_lines.append(line)

    if len(message_lines) > 0:
        messages.append(MKDocsMessage.init_raw_message("\n".join(message_lines), ''))

    # format the channel (format all messages)
    formatted_channel = '# {}\n'.format(channel_name.replace('-', ' ').capitalize())
    for message in messages:
        message.format_bot_command()
        message.format_content()
        formatted_channel = '{}{}'.format(formatted_channel, message)

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

            logger.debug(f"formatting {category_name}/{channel_name}.md")
            generate_channel_source(channel_dir, source_dir, category_name, channel_name)

            category_channels.append('pvme-guides/{}/{}.md'.format(category_name, channel_name))

        mkdocs_nav.append({formatted_category: category_channels})

    update_mkdocs_nav(mkdocs_yml, mkdocs_nav)

    return 0


if __name__ == '__main__':
    # for debugging
    logging.basicConfig()
    logging.getLogger('formatter.mkdocs').level = logging.DEBUG
    logging.getLogger('formatter.rules').level = logging.DEBUG
    logging.getLogger('formatter.util').level = logging.DEBUG

    generate_sources('../pvme-guides', '../docs', '../mkdocs.yml')
    pass
