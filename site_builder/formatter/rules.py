"""
Collection of all message formatting rules.
"""
import re
from abc import ABC, abstractmethod
import os
import logging
from pathlib import Path

from site_builder.formatter.pvme_settings import PVMESpreadsheetData, PVMEUserData, PVMERoleData, PVMEChannelData
from site_builder.formatter.attachment_embed import get_attachment_from_url

__all__ = ['Emoji', 'Insert', 'EmbedLink', 'LineBreak', 'DiscordWhiteSpace', 'PVMESpreadSheet',
           'DiscordChannelID', 'DiscordUserID', 'DiscordRoleID', 'MarkdownLink', 'EmbedCodeBlock',
           'MarkdownLineSpacing', 'EmptyLines', 'EmbedCodeInline', 'ToCPinsMention']

logger = logging.getLogger('file_formatter.rules')
logger.level = logging.WARN


class AbsFormattingRule(ABC):
    @staticmethod
    @abstractmethod
    def format_content(content):
        raise NotImplementedError()

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
    """Format "$data_pvme:Perks!H11$" and "$data_pvme:gptotal_archglacor_200ks$" to the price from the pvme-guides spreadsheet."""
    PATTERN = re.compile(r"\$data_pvme:([^$]+)\$")
    PVME_SPREADSHEET_DATA = PVMESpreadsheetData()

    @staticmethod
    def format_content(content):
        matches = [match for match in re.finditer(PVMESpreadSheet.PATTERN, content)]
        for match in reversed(matches):
            cell_id = match.group(1)
            if match_cell := re.match(r"([^!]+)!([A-Za-z]+)([1-9]\d*)", cell_id):
                price_formatted = PVMESpreadSheet.PVME_SPREADSHEET_DATA.cell(match_cell.group(1), match_cell.group(2),
                                                                            int(match_cell.group(3)))
            else:
                price_formatted = PVMESpreadSheet.PVME_SPREADSHEET_DATA.cell_alias(cell_id)
            content = content[:match.start()] + price_formatted + content[match.end():]
        return content


class DiscordChannelID(AbsFormattingRule):
    """Format '<#534514775120412692>' to '[araxxor-melee](../../high-tier-pvm/araxxor-melee.md)'."""
    CUR_FILE: Path = None
    PATTERN = re.compile(r"<#(\d{17,20})>")
    CHANNEL_LOOKUP = PVMEChannelData()
    INVALID_CHANNEL_LOOKUP = {
        '1021152606455873686': 'pvm-help-forums',
        '1019648841965916220': 'vod-reviews',
        '656898197561802760': 'pvm-help',
        '1020050459618185328': 'deleted-channel',
        '611748860746006528': 'deleted-channel',
        '1020050319457132654': 'deleted-channel',
        '1020052687070445618': 'deleted-channel',
        '1020050385676812368': 'deleted-channel',
        '1024671502064431164': 'deleted-channel',
        '1020034741644316754': 'deleted-channel',
        '1020034711491444737': 'deleted-channel',
        '1020034653945593857': 'deleted-channel',
        '1020050437963010149': 'deleted-channel',
        '534514775120412692': 'deleted-channel',
        '776298051567353917': 'deleted-channel',
        '959583319853506680': 'deleted-channel',
        '1020043790582554634': 'deleted-channel',
        '1020043833955864606': 'deleted-channel',
        '892084479953358869': 'deleted-channel',
        '858836097608712202': 'deleted-channel',
        '858836169864511488': 'deleted-channel',
        '1020046883575566376': 'deleted-channel',
        '1020052936631533638': 'deleted-channel',
        '1020049593901264946': 'deleted-channel',
        '1020047304075513857': 'deleted-channel',
        '1020047234328436858': 'deleted-channel',
        '796067569735041046': 'deleted-channel',
        '534563158304620564': 'bot-commands',
        '1020853673317908500': 'suggestions',
        '537042924026724353': 'to-be-archived-suggestions',
        '1020024227115573369': 'rs3-slayer',

        '1020045708746833930': 'upgrade-order',         # todo: forum overview
        '827692629197324348': 'role-submissions',
        '53565476994822964': 'server-announcements',
        '771436827214086154': 'guide-media-upload-and-request',
        '1152990486714388622': 'editing-jobs',
        '724129126314803230': 'editors-chat',

        '992535252276887602': 'RuneScape -> recruitment-all',
        '723915055976153138': 'affiliates',
        '944775418844688464': 'RuneScape -> runescape-questions',
        '1197226494523621376': 'RuneScape -> looking-for-group',
        '1081013603194380359': 'dpm-advice-basic',      # todo: forum overview
        
        '1141139913610362940': 'other-social',      # note: forum overview but social channels only
        '1141048675620102154': 'osrs-general',
        '1082182941762924595': 'general',
        '538137911292329986': 'achievements',
        '536062588090318850': 'theorycrafting',
        '557699151291351060': 'pvm-fails',
        '935213935999737916': 'rs3-general',

        '1128137032418467890': 'ability-information',   # todo: forum overview
        '1020418878121197678': 'afk-guides',            # todo: forum overview
        
        '1020025399079600178': 'angel-of-death-7s',     # todo: forum overview

        '1020050703017844856': 'unknown',               # note: unknown in disc

        '1251377290995306516': 'unknown',               # note: unknown in disc

        # '535654769948229643': 'server-announcements',   # note: not sure why server-announcements has 2 ids

        '1020841129064812646': 'editor-resources',      # todo: forum overview
        '1020841226414604308': 'github-tutorials',      # todo: forum overview

        '689575078698287152': 'bot-test',
        '1096801858535833602': 'unknown',               # note: unknown but clickable thread
        '1162558489533612063': 'unknown',               # note: unknown but clickable thread

        '1153050298978422925': 'unknown',               # note: unknown in disc
        '820143052227346442': 'mod-mail',
        '1019739867032330290': 'dpm-advice',            # todo: forum overview
        '535654769948229643': 'server-announcements',
    }

    @staticmethod
    def format_content(content):
        matches = [match for match in re.finditer(DiscordChannelID.PATTERN, content)]
        for index, match in enumerate(reversed(matches)):
            channel = DiscordChannelID.CHANNEL_LOOKUP.get(match.group(1))
            if channel:
                # name = channel['name']
                # txt_path = channel['path']
                # path = f"{os.path.dirname(txt_path)}/{name}"
                # link = f"[#{name}](../../{path})"
                name = channel['name']
                txt_file = Path(channel['path'])
                # todo: work-around relative links, check if absolute links work
                relative_path = '../' * (len(DiscordChannelID.CUR_FILE.parts) - 1) + txt_file.with_suffix('').as_posix()
                link = f"[#{name}]({relative_path})"
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
    """Format '<@213693069764198401>' to '@Piegood'."""
    PATTERN = re.compile(r"<@!?([0-9]{17,20})>")
    USER_LOOKUP = PVMEUserData()

    @staticmethod
    def format_content(content):
        matches = [match for match in re.finditer(DiscordUserID.PATTERN, content)]
        for index, match in enumerate(reversed(matches)):
            user = f"@{DiscordUserID.USER_LOOKUP.get(match.group(1), 'Unknown user')}"
            if user == '@Unknown user':
                logger.warning(f"unknown user {match.group(1)}")
            content = content[:match.start()] + user + content[match.end():]
        return content


class DiscordRoleID(AbsFormattingRule):
    """Format '<@&645851931842969611>' to '@Araxxor Initiate'."""
    PATTERN = re.compile(r"<@&([0-9]{17,20})>")
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
    PATTERN = re.compile(r"\[([^]]+)]\(\s*(http[s]?://[^\s()]+)\s*\)")

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


class ToCPinsMention(AbsFormattingRule):
    PATTERNS = [
        re.compile(r"\*Note: a \*\*Table of Contents\*\* can be found in the pins\.\*", flags=re.IGNORECASE),
        re.compile(r"\*\*The Table of Contents with navigation links for this channel can be found in the pinned messages\.\*\*", flags=re.IGNORECASE),
        # re.compile(r"\*Note: Use the \^\^\*\*Table of Contents\*\*\^\^ present at the bottom of the channel, or in the pinned comments, to quickly navigate through this channel and find the information you are looking for\.\*", flags=re.IGNORECASE),
    ]

    @staticmethod
    def format_content(content):
        for pattern in ToCPinsMention.PATTERNS:
            content = re.sub(pattern, '', content)
        return content
