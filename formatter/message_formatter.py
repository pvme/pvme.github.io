"""Process of converting raw text from a guide.txt file to formatted text in a guide.md
"""
from dataclasses import dataclass, field

from formatter.rules import *
from formatter.discord_embed import EmbedHTMLGenerator, embed_str_to_dict
from formatter.util import generate_embed
from typing import List


DEFAULT_FORMAT_SEQUENCE = [
    EmptyLines,
    Section,
    LineBreak,
    EmbedLink,
    Emoji,
    Insert,
    DiscordWhiteSpace,
    PVMESpreadSheet,
    DiscordChannelID,
    DiscordUserID,
    DiscordRoleID,
    MarkdownLineSpacing,
]


@dataclass
class RawMessage:
    """Raw messages split by bot command that are parsed directly from a guide.txt."""
    content: str = None
    bot_command: str = None

    @classmethod
    def from_message_lines(cls, message_lines: list, bot_command: str):
        if len(message_lines) == 0:
            # work-around to avoid unnecessary empty lines
            return cls(bot_command=bot_command)
        return cls('\n'.join(message_lines), bot_command)


@dataclass
class FormattedMessage:
    """Formatted messages containing markdown/HTML that are written to guide.md"""
    content: str = ''
    embed: str = ''
    bot_command: str = ''
    attachment_embeds: list = field(default_factory=list)

    def __str__(self):
        bot_command_spacing = '\n' if self.bot_command != '' else ''
        return '{}\n{}\n{}{}{}\n'.format(
            self.content,
            '\n\n'.join(self.attachment_embeds),
            self.embed,
            bot_command_spacing,
            self.bot_command)


class MessageFormatter:
    """Formats raw message directly parsed from guide.txt to formatted message in guide.md"""
    def __init__(self, raw_message: RawMessage):
        self.__raw_message: RawMessage = raw_message
        self.__formatted_message: FormattedMessage = FormattedMessage()

    @property
    def formatted_message(self):
        return self.__formatted_message

    def __format_embed_message(self):
        embed_json = embed_str_to_dict(self.__raw_message.content)
        self.__raw_message.content = embed_json.get('content', None)  # todo: confirm "content" field is allowed
        self.__formatted_message.embed = str(EmbedHTMLGenerator(self.parse_embed_json(embed_json,
                                                                                      self.__raw_message.content)))

    def __format_bot_command(self):
        if self.__raw_message.bot_command == '.':
            self.__formatted_message.bot_command = ''

        elif self.__raw_message.bot_command.startswith((".tag:", ".pin:", ".tag:")):
            self.__formatted_message.bot_command = ''

        elif self.__raw_message.bot_command.startswith((".img:", ".file:")):
            link = self.__raw_message.bot_command.split(':', 1)
            self.__formatted_message.bot_command = generate_embed(link[1])

        elif self.__raw_message.bot_command == '.embed:json':
            self.__formatted_message.bot_command = ''

        else:
            raise ValueError(f"Unknown bot command: {self.__raw_message.bot_command}")

    def __format_message(self, format_sequence: List):
        self.__format_bot_command()

        if not self.__raw_message.content and self.__raw_message.content != '':
            # todo: check for content != '' SHOULD be redundant and removed
            return

        # only format sections that are not in a code block
        sections_split_by_code_block = self.split_code_block_sections(self.__raw_message.content)
        for index, section in enumerate(sections_split_by_code_block):
            if index % 2 == 0:
                # section should be formatted
                content, attachment_embeds = self.apply_formatting_rules(section, format_sequence)
                self.__formatted_message.content += content
                self.__formatted_message.attachment_embeds.extend(attachment_embeds)
            else:
                # section inside code block, don't apply formatting
                # todo: amount of padding depends on code block
                self.__formatted_message.content += f"\n```\n{section}\n```\n"

    def format(self, format_sequence: List = None):
        format_sequence = format_sequence if format_sequence else DEFAULT_FORMAT_SEQUENCE

        if self.__raw_message.bot_command == '.embed:json':
            self.__format_embed_message()

        # embed:json can have content field
        self.__format_message(format_sequence)

    @staticmethod
    def apply_formatting_rules(content: str, format_sequence: List) -> (str, List[str]):
        attachment_embeds = []
        for formatter_ in format_sequence:
            if repr(formatter_) == "<class 'formatter.rules.EmbedLink'>":
                # todo: change to actual detection
                content = EmbedLink.format_content(content, attachment_embeds)
            else:
                content = formatter_.format_content(content)

        return content, attachment_embeds

    @staticmethod
    def split_code_block_sections(content: str) -> List[str]:
        return content.split('```')

    @staticmethod
    def parse_embed_json(embed_json: dict, content: str) -> dict:
        """Parse embed from various allowed structures."""
        # todo: some of these rule checks should be part of syntax checker
        if 'embed' in embed_json and isinstance(embed_json['embed'], dict):
            # key "embed" pointing to the embed
            return embed_json['embed']
        elif 'embeds' in embed_json and isinstance(embed_json['embeds'], list):
            # key "embeds" pointing to arrow with length 1 containing the embed
            return embed_json['embeds']
        elif (content == '' and len(embed_json.keys()) > 0) or (content != '' and len(embed_json.keys()) > 1):
            # the structure is the embed itself
            return embed_json
        else:
            raise ValueError(f"invalid embed format {embed_json}")


class RawMessageParser:
    """Obtains all messages from the contents of a guide"""
    def __init__(self, text: str):
        self.__text: str = text
        self.__raw_messages: List = []

    @property
    def raw_messages(self):
        return self.__raw_messages

    @staticmethod
    def line_is_bot_command(line: str) -> bool:
        return line.startswith('.') and not line.startswith('..')

    @staticmethod
    def message_is_toc(message_lines: List[str]) -> bool:
        return len(message_lines) >= 3 and 'table of contents' in message_lines[2].lower()

    def parse(self):
        message_lines = []

        # for line in self.__text.split('\n'):
        for line in self.__text.splitlines():
            if self.line_is_bot_command(line):
                if not self.message_is_toc(message_lines):
                    self.__raw_messages.append(RawMessage.from_message_lines(message_lines, line))

                message_lines = []
            else:
                message_lines.append(line)

        if len(message_lines) > 0:
            # add last message if it's not closed by a bot command
            self.__raw_messages.append(RawMessage.from_message_lines(message_lines, '.'))
