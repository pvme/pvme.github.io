"""
Collection of all message formatting rules.
"""
import re
from abc import ABC, abstractmethod
import os
import logging

from gspread.utils import a1_to_rowcol

import formatter.util

__all__ = ['PVMEBotCommand', 'Section', 'Emoji', 'Insert', 'EmbedLink', 'LineBreak', 'DiscordWhiteSpace',
           'CodeBlock', 'PVMESpreadSheet', 'DiscordChannelID', 'DiscordUserID', 'DiscordRoleID']

logger = logging.getLogger('formatter.rules')
logger.level = logging.WARN


class Sphinx(ABC):
    @staticmethod
    @abstractmethod
    def format_sphinx_rst(message, doc_info):
        raise NotImplementedError()


class MKDocs(ABC):
    @staticmethod
    @abstractmethod
    def format_mkdocs_md(message):
        raise NotImplementedError()


class PVMEBotCommand(MKDocs):
    """Format lines starting with . (bot commands)."""
    @staticmethod
    def format_mkdocs_md(message):
        if not message.bot_command:
            return

        if message.bot_command == '.':
            message.bot_command = ''
        elif message.bot_command == "..":
            message.bot_command = '.'
        elif message.bot_command.startswith((".tag:", ".pin:", ".tag:")):
            message.bot_command = ''
        elif message.bot_command.startswith((".img:", ".file:")):
            # todo: temporary parsing to get a general idea
            link = message.bot_command.split(':', 1)
            message.bot_command = formatter.util.generate_embed(link[1])


class Section(MKDocs):
    """Format lines starting with > __**section**__ to ## section."""
    PATTERN = re.compile(r"(?:^|\n)>\s(.+?)(?=\n|$)")

    @staticmethod
    def format_mkdocs_md(message):
        matches = [match for match in re.finditer(Section.PATTERN, message.content)]

        for match in reversed(matches):
            section_name = re.sub(r"[*_]*", '', match.group(1))
            section_name_formatted = "## {}".format(section_name)

            # remove ':' at the end of a section name to keep ry happy
            if section_name_formatted.endswith(':'):
                section_name_formatted = section_name_formatted[:-1]

            message.content = message.content[:match.start()] + section_name_formatted + message.content[match.end():]


class Emoji(MKDocs):
    """<concBlast:1234> -> <img src="https://cdn.discordapp.com/emojis/535533809924571136.png?v=1" class="emoji">"""
    PATTERNS = [(re.compile(r"<:([^:]{2,}):([0-9]+)>"), ".png"),
                (re.compile(r"<:a:([^:]+):([0-9]+)>"), ".gif")]

    @staticmethod
    def format_mkdocs_md(message):
        for pattern, extension in Emoji.PATTERNS:
            matches = [match for match in re.finditer(pattern, message.content)]
            for match in reversed(matches):
                emoji_formatted = "<img title=\"{}\" class=\"emoji\" alt=\"{}\" src=\"https://cdn.discordapp.com/emojis/{}{}?v=1\">".format(match.group(1), match.group(1), match.group(2), extension)
                message.content = message.content[:match.start()] + emoji_formatted + message.content[match.end():]


class Insert(MKDocs):
    PATTERN = re.compile(r"__")

    @staticmethod
    def format_mkdocs_md(message):
        message.content = re.sub(Insert.PATTERN, '^^', message.content)


class EmbedLink(MKDocs):
    # modified Django link regex with embed and () link detection
    PATTERN = re.compile(
        r"(?:[^<])"
        r"((?:http|ftp)s?://"
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"
        r"localhost|"           # localhost...
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|"      
        r"\[?[A-F0-9]*:[A-F0-9:]+\]?)"              
        r"(?::\d+)?"            
        r"(?:/?|[/?]\S+)"
        r"(?:[^ )\n\t\r]*))", re.IGNORECASE)

    @staticmethod
    def format_mkdocs_md(message):
        # todo: character at the start of the embed is removed (e.g. '(' in github for contribution quick start)
        matches = [match for match in re.finditer(EmbedLink.PATTERN, message.content)]
        for match in reversed(matches):
            url_formatted = "<{}>".format(match.group(1))
            message.content = message.content[:match.start() + 1] + url_formatted + message.content[match.end():]

        for match in matches:
            embed = formatter.util.generate_embed(match.group(1))
            if embed:
                message.embeds.append(embed)


class LineBreak(MKDocs):
    PATTERN = re.compile(r"_ _")

    @staticmethod
    def format_mkdocs_md(message):
        message.content = re.sub(LineBreak.PATTERN, '', message.content)


class DiscordWhiteSpace(MKDocs):
    """Converts whitespace and tabs that would normally be converted to a single space in html/markdown
    to a special "empty" character. For now this is used over <pre> </pre> and &nbsp; due to inline code blocks

    todo: use &nbsp; instead of the weirdchamp "empty" character, this requires detecting code blocks
    """
    @staticmethod
    def format_mkdocs_md(message):
        message.content = re.sub(r"\t", '    ‎', message.content)

        matches = [match for match in re.finditer(r"( {2,})", message.content)]
        for match in reversed(matches):
            line_spaces = ' ‎' * len(match.group(1))
            message.content = message.content[:match.start()] + line_spaces + message.content[match.end():]

        message.content = re.sub(r"^ ", ' ‎', message.content)


class CodeBlock(MKDocs):
    # todo: current approach adds enter to start and end of block, consider improving this
    PATTERN = re.compile(r"```")

    @staticmethod
    def format_mkdocs_md(message):
        message.content = re.sub(CodeBlock.PATTERN, '\n```\n', message.content)


class PVMESpreadSheet(MKDocs):
    """Format "$data_pvme:Perks!H11$" to the price from the pvme-guides spreadsheet."""
    PATTERN = re.compile(r"\$data_pvme:([^!]+)!([^$]+)\$")

    @staticmethod
    def format_mkdocs_md(message):
        matches = [match for match in re.finditer(PVMESpreadSheet.PATTERN, message.content)]
        for match in reversed(matches):
            worksheet_data = formatter.util.obtain_pvme_spreadsheet_data(match.group(1))
            row, column = a1_to_rowcol(match.group(2))
            if worksheet_data:
                price_formatted = "{}".format(worksheet_data[row-1][column-1])
            else:
                price_formatted = "N/A"

            message.content = message.content[:match.start()] + price_formatted + message.content[match.end():]


class DiscordChannelID(MKDocs):
    """Format '<#534514775120412692>' to '[araxxor-melee](../../high-tier-pvm/araxxor-melee.md)'."""
    PATTERN = re.compile(r"<#([0-9]{18})>")
    CHANNEL_LOOKUP = formatter.util.parse_channel_id_file()

    @staticmethod
    def format_mkdocs_md(message):
        matches = [match for match in re.finditer(DiscordChannelID.PATTERN, message.content)]
        for index, match in enumerate(reversed(matches)):
            path = DiscordChannelID.CHANNEL_LOOKUP.get(match.group(1))
            if path:
                relative_file = f"../{path}.md"
                # name = os.path.basename(path).replace('-', ' ').capitalize()  # 'Araxxor melee'
                name = f"#{os.path.basename(path)}"
                link = f"[{name}]({relative_file})"
            else:
                # link = "[Unknown channel]()"
                link = "[#unknown-channel]()"
                logger.warning(f"unknown channel {match.group(1)}")

            message.content = message.content[:match.start()] + link + message.content[match.end():]


class DiscordUserID(MKDocs):
    """Format '<@213693069764198401>' to '#Piegood'."""
    PATTERN = re.compile(r"<@!?([0-9]{18})>")
    USER_LOOKUP = formatter.util.parse_user_id_file()

    @staticmethod
    def format_mkdocs_md(message):
        matches = [match for match in re.finditer(DiscordUserID.PATTERN, message.content)]
        for index, match in enumerate(reversed(matches)):
            user = f"#{DiscordUserID.USER_LOOKUP.get(match.group(1), 'Unknown user')}"
            if user == '#Unknown user':
                logger.warning(f"unknown user {match.group(1)}")
            message.content = message.content[:match.start()] + user + message.content[match.end():]


class DiscordRoleID(MKDocs):
    """Format '<@&645851931842969611>' to '@Araxxor Initiate'."""
    PATTERN = re.compile(r"<@&([0-9]{18})>")
    ROLE_LOOKUP = formatter.util.parse_role_id_file()

    @staticmethod
    def format_mkdocs_md(message):
        matches = [match for match in re.finditer(DiscordRoleID.PATTERN, message.content)]
        for index, match in enumerate(reversed(matches)):
            role = DiscordRoleID.ROLE_LOOKUP.get(match.group(1), ('Unknown role', None))
            if role[0] == 'Unknown role':
                logger.warning(f"unknown role {match.group(1)}")
            role_formatted = f"<code style=\"{role[1]}\">@{role[0]}</code>"
            message.content = message.content[:match.start()] + role_formatted + message.content[match.end():]