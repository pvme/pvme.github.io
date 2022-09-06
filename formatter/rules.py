"""
Collection of all message formatting rules.
"""
import re
from abc import ABC, abstractmethod
import os
import logging

from formatter.pvme_settings import PVMESpreadsheetData, PVMEUserData, PVMERoleData, PVMEChannelData
from formatter.attachment_embed import get_attachment_from_url

__all__ = ['Section', 'Emoji', 'Insert', 'EmbedLink', 'LineBreak', 'DiscordWhiteSpace', 'PVMESpreadSheet',
           'DiscordChannelID', 'DiscordUserID', 'DiscordRoleID', 'MarkdownLink', 'EmbedCodeBlock',
           'MarkdownLineSpacing', 'EmptyLines', 'EmbedCodeInline']

logger = logging.getLogger('formatter.rules')
logger.level = logging.WARN


class AbsFormattingRule(ABC):
    @staticmethod
    @abstractmethod
    def format_content(content):
        raise NotImplementedError()


class Section(AbsFormattingRule):
    """Format lines starting with > __**section**__ to ## section."""
    PATTERN = re.compile(r"(?:^|\n)>\s(.+?)(?=\n|$)")

    @staticmethod
    def format_content(content):
        matches = [match for match in re.finditer(Section.PATTERN, content)]

        for match in reversed(matches):
            section_name = re.sub(r"[*_]*", '', match.group(1))
            section_name_formatted = "## {}".format(section_name)

            # remove ':' at the end of a section name to keep ry happy
            if section_name_formatted.endswith(':'):
                section_name_formatted = section_name_formatted[:-1]

            content = content[:match.start()] + section_name_formatted + content[match.end():]
        return content


class Emoji(AbsFormattingRule):
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


class Insert(AbsFormattingRule):
    PATTERN = re.compile(r"__")

    @staticmethod
    def format_content(content):
        return re.sub(Insert.PATTERN, '^^', content)


class EmbedLink:
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
    def format_content(content, attachment_embeds):
        matches = [match for match in re.finditer(EmbedLink.PATTERN, content)]
        for match in reversed(matches):
            url_formatted = "<{}>".format(match.group(1))
            spacer = 1 if match.start() > 0 else 0
            content = content[:match.start() + spacer] + url_formatted + content[match.end():]

        for match in matches:
            embed = get_attachment_from_url(match.group(1))
            if embed:
                attachment_embeds.append(embed)

        # todo: better option that doesn't change purpose of format_content()
        return content


class LineBreak(AbsFormattingRule):
    PATTERN = re.compile(r"_ _")

    @staticmethod
    def format_content(content):
        return re.sub(LineBreak.PATTERN, '', content)


class DiscordWhiteSpace(AbsFormattingRule):
    """Converts whitespace and tabs that would normally be converted to a single space in html/markdown
    to a special "empty" character. For now this is used over <pre> </pre> and &nbsp; due to inline code blocks

    todo: use &nbsp; instead of the weirdchamp "empty" character, this requires detecting code blocks
    """
    @staticmethod
    def format_content(content):
        content = re.sub(r"\t", '    ‎', content)

        matches = [match for match in re.finditer(r"( {2,})", content)]
        for match in reversed(matches):
            line_spaces = ' ‎' * len(match.group(1))
            content = content[:match.start()] + line_spaces + content[match.end():]

        content = re.sub(r"^ ", ' ‎', content)
        return content


class PVMESpreadSheet(AbsFormattingRule):
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


class DiscordChannelID(AbsFormattingRule):
    """Format '<#534514775120412692>' to '[araxxor-melee](../../high-tier-pvm/araxxor-melee.md)'."""
    PATTERN = re.compile(r"<#([0-9]{18})>")
    CHANNEL_LOOKUP = PVMEChannelData()
    INVALID_CHANNEL_LOOKUP = {
        '656898197561802760': 'pvm-help',
        '656914685152722954': 'vod-review-submission',
        '534563158304620564': 'bot-commands',
        '537042924026724353': 'suggestions',
        '185315527571406848': 'deleted-channel'
    }

    @staticmethod
    def format_content(content):
        matches = [match for match in re.finditer(DiscordChannelID.PATTERN, content)]
        for index, match in enumerate(reversed(matches)):
            channel = DiscordChannelID.CHANNEL_LOOKUP.get(match.group(1))
            if channel:
                name = channel['name']
                txt_path = channel['path']
                path = f"{os.path.dirname(txt_path)}/{name}"
                link = f"[#{name}](../../{path})"
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


class DiscordUserID(AbsFormattingRule):
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


class DiscordRoleID(AbsFormattingRule):
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


class MarkdownLineSpacing(AbsFormattingRule):
    @staticmethod
    def format_content(content):
        lines = content.splitlines()
        return '\n\n'.join(lines)


class EmptyLines(AbsFormattingRule):
    @staticmethod
    def format_content(content):
        lines = content.split('\n')
        lines_formatted = ['&#x200b;' if len(line) == 0 else line for line in lines]
        return '\n'.join(lines_formatted)


class MarkdownLink(AbsFormattingRule):
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


class EmbedCodeBlock(AbsFormattingRule):
    """Format: ```cool text``` to <pre><code>cool text</code></pre>
    NOTE: couldn't use fenced_code python-markdown extension here as it was inconsistent with formatting.
    todo: code block margin
    """
    PATTERN = re.compile(r"```\n?")

    @staticmethod
    def format_content(content):
        matches = [match for match in re.finditer(EmbedCodeBlock.PATTERN, content)]
        for index, match in enumerate(reversed(matches)):
            if index % 2:
                # code block start
                # optional: discord CSS
                # content = content[:match.start()] + "<pre><code class=\"h1js\">" + content[match.end():]
                content = content[:match.start()] + "<pre><code>" + content[match.end():]
            else:
                # code block end
                content = content[:match.start()] + "</code></pre>" + content[match.end():]

        return content


class EmbedCodeInline(AbsFormattingRule):
    PATTERN = re.compile(r"`")

    @staticmethod
    def format_content(content):
        matches = [match for match in re.finditer(EmbedCodeInline.PATTERN, content)]
        for index, match in enumerate(reversed(matches)):
            if index % 2:
                # inline code start
                content = content[:match.start()] + "<code class=\"embed-code-inline\">" + content[match.end():]
            else:
                # inline code end
                content = content[:match.start()] + "</code>" + content[match.end():]

        return content
