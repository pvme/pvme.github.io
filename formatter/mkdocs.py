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
import json
import pathlib
from copy import deepcopy
from dataclasses import dataclass, field

import ruamel.yaml

from formatter.rules import *
from formatter.discord_embed import EmbedHTMLGenerator, parse_embed_json

logger = logging.getLogger('formatter.mkdocs')
logger.level = logging.WARN

MAIN_PATH = pathlib.Path(__file__).parent.parent.absolute()

CATEGORY_SEQUENCE = [
    'getting-started',
    'upgrading-info',
    'miscellaneous-information',
    'dpm-advice',
    'basic-guides',
    'low-tier-pvm',
    'mid-tier-pvm',
    'high-tier-pvm',
    'nex-aod',
    'elite-dungeons',
    'gwd3',
    'vorago',
    'solak',
    'telos',
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

JSON_EMBED_FORMAT_SEQUENCE = [
    LineBreak,
    Emoji,
    DiscordChannelID,
    DiscordUserID,
    DiscordRoleID
]


@dataclass
class JsonEmbed(object):
    raw: dict = field(default_factory=dict)
    content: str = field(default='')
    embeds: list = field(default_factory=list)  # unused


class MKDocsMessage(object):
    def __init__(self, content, embeds, bot_command, json_embed=None):
        self.content = content
        self.embeds = embeds if embeds else list()
        # todo: replace bot_command, bot_command_formatted with single bot_command dataclass
        self.bot_command = bot_command
        self.bot_command_formatted = ''
        self.json_embed = JsonEmbed(json_embed)

    @classmethod
    def init_raw_message(cls, content, bot_command):
        if bot_command == '.embed:json':
            # extract 'content' (normal message) and embed from .embed:json
            json_dict = parse_embed_json(content)
            content = json_dict.get('content', '')
            json_embed = MKDocsMessage.parse_json_embed(json_dict, content)
        else:
            json_embed = None

        return cls(content, None, bot_command, json_embed)

    @staticmethod
    def parse_json_embed(json_dict, content):
        """Parse embed (dict) structure based on the following rules:

        - the json object itself can be an embed
        - the json object can have the key "embed" pointing to the embed
        - or the json object can also have the key "embeds" pointing to an array of length 1, containing an embed
        """
        json_dict = deepcopy(json_dict)
        if 'embed' in json_dict and type(json_dict['embed']) == dict:
            json_embed = json_dict['embed']
        elif 'embeds' in json_dict and type(json_dict['embeds'] == list):
            json_embed = json_dict['embeds'][0] if len(json_dict['embeds']) >= 1 else None
        elif (content == '' and len(json_dict.keys()) > 0) or (content != '' and len(json_dict.keys()) > 1):
            json_embed = json_dict
        else:
            json_embed = None

        return json_embed

    def format_bot_command(self):
        PVMEBotCommand.format_mkdocs_md(self)

    def format_content(self, format_sequence: list = None):
        format_sequence = format_sequence if format_sequence else DEFAULT_FORMAT_SEQUENCE

        for formatter in format_sequence:
            formatter.format_mkdocs_md(self)

    def format_json_embed(self):
        if self.json_embed.raw:
            self.json_embed.content = str(EmbedHTMLGenerator(self.json_embed.raw))
            for formatter in JSON_EMBED_FORMAT_SEQUENCE:
                formatter.format_mkdocs_md(self.json_embed)

    def __str__(self):
        # todo: remove unnecessary spaces (won't affect html report but it's a bit cleaner)
        bot_command_spacing = '\n' if self.bot_command_formatted != '' else ''
        return '{}\n{}\n{}{}{}\n'.format(
            '\n\n'.join(self.content.splitlines()),
            '\n\n'.join(self.embeds),
            self.json_embed.content,
            bot_command_spacing,
            self.bot_command_formatted)


def generate_channel_source(channel_txt_file, source_dir, category_name, channel_name):
    with open(channel_txt_file, 'r', encoding='utf-8') as file:
        raw_data = file.read()

    # obtain all the messages using the . separator
    # todo: separate function
    messages = list()
    message_lines = list()
    for line in raw_data.splitlines():
        if line.startswith('.'):
            # ignore table of contents because there already is one
            if len(message_lines) < 3 or 'table of contents' not in message_lines[2].lower():
                messages.append(MKDocsMessage.init_raw_message("\n".join(message_lines), line))
            message_lines = list()
        else:
            message_lines.append(line)

    if len(message_lines) > 0:
        messages.append(MKDocsMessage.init_raw_message("\n".join(message_lines), ''))

    # format the channel (format all messages)
    # todo: separate function
    formatted_channel = '# {}\n'.format(channel_name.replace('-', ' ').capitalize())
    for message in messages:
        message.format_bot_command()
        message.format_content()
        message.format_json_embed()
        formatted_channel = '{}{}'.format(formatted_channel, message)

    # write the formatted channel data to guide.md
    with open('{}/{}/pvme-guides/{}/{}.md'.format(MAIN_PATH, source_dir, category_name, channel_name), 'w', encoding='utf-8') as file:
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


def generate_sources() -> int:
    # (clear) + create the source/pvme-guides directory (only really needed for debugging)
    source_dir = 'docs'
    if os.path.isdir('{}/{}/pvme-guides'.format(MAIN_PATH, source_dir)):
        shutil.rmtree('{}/{}/pvme-guides'.format(MAIN_PATH, source_dir), ignore_errors=True)

    os.mkdir('{}/pvme-guides'.format(source_dir))

    with open(f'{MAIN_PATH}/pvme-settings/channels.json', 'r', encoding='utf-8') as file:
        channel_data = json.load(file)
        channel_map = { channel['path']: channel['name'] for channel in channel_data }

    mkdocs_nav = list()     # contents of the mkdocs.yml nav:

    # only search for categories in category sequence, automatically excludes unused categories
    for category_name in CATEGORY_SEQUENCE:
        category_dir = '{}/pvme-guides/{}'.format(MAIN_PATH, category_name)

        # exclude non-directories like README.md and LICENSE
        if not os.path.isdir(category_dir):
            continue

        os.mkdir('{}/{}/pvme-guides/{}'.format(MAIN_PATH, source_dir, category_name))

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

    update_mkdocs_nav('mkdocs.yml', mkdocs_nav)

    return 0


if __name__ == '__main__':
    # for debugging
    logging.basicConfig()
    logging.getLogger('formatter.mkdocs').level = logging.DEBUG
    logging.getLogger('formatter.rules').level = logging.DEBUG
    logging.getLogger('formatter.util').level = logging.DEBUG

    generate_sources()
