"""
Collection of all message formatting rules.
"""
import re
from abc import ABC, abstractmethod
import os
import logging

from formatter.pvme_settings import PVMESpreadsheetData, PVMEUserData, PVMERoleData, PVMEChannelData

import formatter.util

__all__ = ['PVMEBotCommand', 'Section', 'Emoji', 'Insert', 'EmbedLink', 'LineBreak', 'DiscordWhiteSpace',
           'CodeBlock', 'PVMESpreadSheet', 'DiscordChannelID', 'DiscordUserID', 'DiscordRoleID', 'MarkdownLink']

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
            message.bot_command_formatted = ''
        elif message.bot_command == "..":
            message.bot_command_formatted = '.'
        elif message.bot_command.startswith((".tag:", ".pin:", ".tag:")):
            message.bot_command_formatted = ''
        elif message.bot_command.startswith((".img:", ".file:")):
            # todo: temporary parsing to get a general idea
            link = message.bot_command.split(':', 1)
            message.bot_command_formatted = formatter.util.generate_embed(link[1])
        elif message.bot_command == '.embed:json':
            message.bot_command_formatted = ''


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
    def format_content(content):
        for pattern, extension in Emoji.PATTERNS:
            matches = [match for match in re.finditer(pattern, content)]
            for match in reversed(matches):
                emoji_formatted = "<img title=\"{}\" class=\"d-emoji\" alt=\"{}\" src=\"https://cdn.discordapp.com/emojis/{}{}?v=1\">".format(match.group(1), match.group(1), match.group(2), extension)
                content = content[:match.start()] + emoji_formatted + content[match.end():]
        return content

    @staticmethod
    def format_mkdocs_md(message):
        message.content = Emoji.format_content(message.content)


class Insert(MKDocs):
    PATTERN = re.compile(r"__")

    @staticmethod
    def format_mkdocs_md(message):
        message.content = re.sub(Insert.PATTERN, '^^', message.content)


class EmbedLink(MKDocs):
    # modified Django link regex with embed and () link detection
    PATTERN = re.compile(
        r"(?:[^<]|^)"
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
        matches = [match for match in re.finditer(EmbedLink.PATTERN, message.content)]
        for match in reversed(matches):
            url_formatted = "<{}>".format(match.group(1))
            spacer = 1 if match.start() > 0 else 0
            message.content = message.content[:match.start() + spacer] + url_formatted + message.content[match.end():]

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
    PATTERN = re.compile(r"\$data_pvme:([^!]+)!([A-Za-z]+)([1-9]\d*)\$")
    PVME_SPREADSHEET_DATA = PVMESpreadsheetData()

    @staticmethod
    def format_content(content):
        matches = [match for match in re.finditer(PVMESpreadSheet.PATTERN, content)]
        for match in reversed(matches):
            price_formatted = PVMESpreadSheet.PVME_SPREADSHEET_DATA.cell_data(match.group(1), match.group(2),
                                                                              int(match.group(3)))
            content = content[:match.start()] + price_formatted + content[match.end():]
        return content

    @staticmethod
    def format_mkdocs_md(message):
        message.content = PVMESpreadSheet.format_content(message.content)


class DiscordChannelID(MKDocs):
    """Format '<#534514775120412692>' to '[araxxor-melee](../../high-tier-pvm/araxxor-melee.md)'."""
    PATTERN = re.compile(r"<#([0-9]{18})>")
    CHANNEL_LOOKUP = PVMEChannelData()
    INVALID_CHANNEL_LOOKUP = {
        '656898197561802760': 'pvm-help',
        '656914685152722954': 'vod-review-submission',
        '534563158304620564': 'bot-commands',
        '537042924026724353': 'suggestions'
    }

    @staticmethod
    def format_content(content):
        matches = [match for match in re.finditer(DiscordChannelID.PATTERN, content)]
        for index, match in enumerate(reversed(matches)):
            path = DiscordChannelID.CHANNEL_LOOKUP.get(match.group(1))
            if path:
                relative_file = path.replace(".txt", "")
                name = os.path.basename(path).replace(".txt", "")
                link = f"[#{name}](../../{relative_file})"
            else:
                channel_name = DiscordChannelID.INVALID_CHANNEL_LOOKUP.get(match.group(1))
                if channel_name:
                    name = channel_name
                else:
                    name = "unknown-channel"
                    logger.warning(f"unknown channel {match.group(1)}")
                link = f"<a href=\"\" class=\"inactiveLink\">#{name}</a>"
            content = content[:match.start()] + link + content[match.end():]
        return content

    @staticmethod
    def format_mkdocs_md(message):
        message.content = DiscordChannelID.format_content(message.content)


class DiscordUserID(MKDocs):
    """Format '<@213693069764198401>' to '#Piegood'."""
    PATTERN = re.compile(r"<@!?([0-9]{18})>")
    USER_LOOKUP = PVMEUserData()

    @staticmethod
    def format_content(content):
        matches = [match for match in re.finditer(DiscordUserID.PATTERN, content)]
        for index, match in enumerate(reversed(matches)):
            user = f"#{DiscordUserID.USER_LOOKUP.get(match.group(1), 'Unknown user')}"
            if user == '#Unknown user':
                logger.warning(f"unknown user {match.group(1)}")
            content = content[:match.start()] + user + content[match.end():]
        return content

    @staticmethod
    def format_mkdocs_md(message):
        message.content = DiscordUserID.format_content(message.content)


class DiscordRoleID(MKDocs):
    """Format '<@&645851931842969611>' to '@Araxxor Initiate'."""
    PATTERN = re.compile(r"<@&([0-9]{18})>")
    ROLE_LOOKUP = PVMERoleData()

    @staticmethod
    def format_content(content):
        matches = [match for match in re.finditer(DiscordRoleID.PATTERN, content)]
        for index, match in enumerate(reversed(matches)):
            role = DiscordRoleID.ROLE_LOOKUP.get(match.group(1), ('Unknown role', 0xFFFFFF))
            if role[0] == 'Unknown role':
                logger.warning(f"unknown role {match.group(1)}")
            role_formatted = f"<code style=\"color: #{role[1]:06X}; background: #{role[1]:06X}30;\">@{role[0]}</code>"
            content = content[:match.start()] + role_formatted + content[match.end():]
        return content

    @staticmethod
    def format_mkdocs_md(message):
        message.content = DiscordRoleID.format_content(message.content)


class MarkdownLink(MKDocs):
    """Format [named links](https://discordapp.com) to
    <a title="" href="https://discordapp.com" target="_blank" rel="noreferrer">named links</a>
    NOTE: only used for formatting embed:json blocks
    """
    PATTERN = re.compile(r"\[([^]]+)]\(\s*(http[s]?://[^)]+)\s*\)")

    @staticmethod
    def format_content(content):
        matches = [match for match in re.finditer(MarkdownLink.PATTERN, content)]
        for match in reversed(matches):
            html_url_formatted = \
                f"<a title=\"\" href=\"{match.group(2)}\" target=\"_blank\" rel=\"noreferrer\">{match.group(1)}</a>"
            content = content[:match.start()] + html_url_formatted + content[match.end():]
        return content

    @staticmethod
    def format_mkdocs_md(message):
        message.content = MarkdownLink.format_content(message.content)
