"""
Python rewrite of: https://github.com/leovoel/embed-visualizer/blob/master/src/components/embed.jsx
Custom Discord markdown -> HTML formatting required because pymdownx.extra md_in_html is not suited to Discord markdown.


Discord meanwhile ignores the formatting for list items.
In the HTML page, the list items have additional spacing between the lines unlike the result in Discord.
"""
import json
import textwrap
from collections import namedtuple
from datetime import datetime
import markdown
from formatter.discord_markdown import DiscordMarkdownExtension
from formatter.rules import *

JSON_EMBED_FORMAT_SEQUENCE = [
    Emoji,
    DiscordChannelID,
    DiscordUserID,
    DiscordRoleID,
    MarkdownLink,
    PVMESpreadSheet,
    EmbedCodeBlock,
    EmbedCodeInline
]
RGB = namedtuple('RGB', 'red green blue')
MD = markdown.Markdown(extensions=[DiscordMarkdownExtension()])


def embed_str_to_dict(json_string):
    """Parse json string and convert it to a dictionary.

    :param str json_string: json formatted string
    :return: dict with same contents and structure as the json string
    :rtype: dict
    :raises ValueError: parsing error
    """
    json_dict = json.loads(json_string)
    return json_dict


def extract_rgb(color):
    """Convert RGB hex value to RGB(red, green, blue) object.

    :param int color: RGB hex code
    :return: RGB(red, green, blue)
    :rtype: namedtuple
    """
    red = (color >> 16) & 0x0ff
    green = (color >> 8) & 0x0ff
    blue = color & 0x0ff
    return RGB(red, green, blue)


def convert_timestamp(iso_timestamp):
    """Convert "2021-06-02T13:23:50.910Z" to "Thu Jun 10th, 2021 at 7:44 AM".

    :param str iso_timestamp: timestamp in "2021-06-02T13:23:50.910Z" format
    :return: timestamp in "Thu Jun 10th, 2021 at 7:44 AM" format
    :rtype: str
    """
    # todo: implement timestamp
    datetime_parsed = datetime.fromisoformat(iso_timestamp[:-1])
    return datetime_parsed.strftime("%a %b %d, %Y at %H:%M %p")


def patched_convert_to_html(text):
    formatted = text
    for formatter in JSON_EMBED_FORMAT_SEQUENCE:
        formatted = formatter.format_content(formatted)
    return MD.convert(formatted)


class HTMLComponents(object):
    """Collection of Discord embed -> HTML formatters."""

    @staticmethod
    def color_pill(color):
        """<div class="embed-color-pill" style="background-color: rgb(47, 152, 246);"></div>"""
        if color:
            rgb = extract_rgb(color)
            background_color = f"rgb({rgb.red}, {rgb.green}, {rgb.blue})"  # background-color: rgb(0, 198, 198)
        else:
            background_color = "undefined"
        return f"<div class=\"embed-color-pill\" style=\"background-color: {background_color};\"></div>"

    @staticmethod
    def title(title, url):
        """<a target="_blank" rel="noreferrer" href="https://discordapp.com" class="embed-title">title</a>"""
        if not title:
            return ''

        if url:
            formatted_title = f"<a target=\"_blank\" rel=\"noreferrer\" href=\"{url}\" class=\"embed-title\">{patched_convert_to_html(title)}</a>"
        else:
            formatted_title = f"<div class=\"embed-title\" >{patched_convert_to_html(title)}</div>"

        return formatted_title

    @staticmethod
    def description(content):
        """<div class="embed-description markup">content</div>"""
        if not content:
            return ''

        return f"<div class=\"embed-description markup\" >{patched_convert_to_html(content)}</div>"

    @staticmethod
    def author(name, url, icon_url):
        """<div class="embed-author"><img src="icon_url" role="presentation" class="embed-author-icon">
            <a target="_blank" rel="noreferrer" href="url" class="embed-author-name">author name</a>
           </div>
        """
        if not name:
            return ''

        if url:
            author_formatted = f"<a target=\"_blank\" rel=\"noreferrer\" href=\"{url}\" class=\"embed-author-name\">{patched_convert_to_html(name)}</a>"
        else:
            author_formatted = f"<span class=\"embed-author-name\" >{patched_convert_to_html(name)}</span>"

        icon_formatted = f"<img src=\"{icon_url}\" role=\"presentation\" class=\"embed-author-icon\">"
        return f"<div class=\"embed-author\">{icon_formatted}{author_formatted}</div>"

    @staticmethod
    def field(name, value, inline):
        """<div class="embed-field">
            <div class="embed-field-name">name</div>
            <div class="embed-field-value markup">value</div>
           </div>
        """
        if not name and not value:
            return ''

        class_name = "embed-field" + (" embed-field-inline" if inline else '')
        name_formatted = f"<div class=\"embed-field-name\" >{patched_convert_to_html(name)}</div>" if name else ''
        value_formatted = f"<div class=\"embed-field-value markup\" >{patched_convert_to_html(value)}</div>" if value else ''

        return f"<div class=\"{class_name}\" >{name_formatted}{value_formatted}</div>"

    @staticmethod
    def thumbnail(url):
        """<img src="url" role="presentation" class="embed-rich-thumb" style="max-width: 80px; max-height: 80px;">"""
        if not url:
            return ''

        return f"<img src={url} role=\"presentation\" class=\"embed-rich-thumb\" style=\"max-width: 80px; max-height: 80px;\"/>"

    @staticmethod
    def image(url):
        """<a class="embed-thumbnail embed-thumbnail-rich"><img class="image" role="presentation" src="url"></a>"""
        if not url:
            return ''

        return f"<a class=\"embed-thumbnail embed-thumbnail-rich\"><img class=\"image\" role=\"presentation\" src=\"{url}\"></a>"

    @staticmethod
    def footer(timestamp, text, icon_url):
        """<div class="embed-footer">
            <img src="icon_url" class="embed-footer-icon" role="presentation" width="20" height="20">
            <span class="embed-footer">footer text | Wed Jun 2nd, 2021 at 3:23 PM</span>
           </div>
        """
        # todo: double check
        if not timestamp and not text:
            return ''

        timestamp_formatted = convert_timestamp(timestamp) if timestamp else ''
        # note: original implementation has no discord > HTML formatting
        text_formatted = patched_convert_to_html(text) if text else ''
        if timestamp_formatted != '':
            text_formatted += f" | {timestamp_formatted}"

        # note: original implementation checks for timestamp and text, would assume only text required ?
        icon_formatted = f"<img src=\"{icon_url}\" class=\"embed-footer-icon\" role=\"presentation\" width=\"20\" height=\"20\">" if icon_url else ''

        return f"<div class=\"embed-footer\">{icon_formatted}<span class=\"embed-footer\">{text_formatted}</span></div>"

    @staticmethod
    def fields(fields):
        """<div  class="embed-fields">
                <div class="embed-field"></div>
                ...
           </div>
        """
        if not fields:
            return ''

        fields_formatted = ""
        for field in fields:
            fields_formatted += HTMLComponents.field(field.get('name'), field.get('value'), field.get('inline'))

        return f"<div class=\"embed-fields\">{fields_formatted}</div>"


class EmbedHTMLGenerator(object):
    """Discord embed -> HTML formatter"""

    def __init__(self, embed):
        """Create EmbedHTMLGenerator object.

        :param dict embed: embed dict containing one or more of the following keys:
            'color', 'title', 'description', 'author', 'thumbnail', 'image', 'footer'
        """
        self.__color_pill = HTMLComponents.color_pill(embed.get('color'))
        self.__title = HTMLComponents.title(embed.get('title'), embed.get('url'))
        self.__description = HTMLComponents.description(embed.get('description'))

        author = embed.get('author', dict())
        self.__author = HTMLComponents.author(author.get('name'), author.get('url'), author.get('icon_url'))
        self.__fields = HTMLComponents.fields(embed.get('fields'))

        thumbnail = embed.get('thumbnail', dict())
        self.__thumbnail = HTMLComponents.thumbnail(thumbnail.get('url'))

        image = embed.get('image', dict())
        self.__image = HTMLComponents.image(image.get('url'))

        footer = embed.get('footer', dict())
        self.__footer = HTMLComponents.footer(embed.get('timestamp'), footer.get('text'), footer.get('icon_url'))

    @classmethod
    def from_json_string(cls, json_string):
        """Create EmbedHTMLGenerator object from a json string.

        :param str json_string: json formatted embed string
        :return: new EmbedHTMLGenerator object
        :rtype: EmbedHTMLGenerator
        """
        json_dict = json.loads(json_string)
        return cls(json_dict.get('embed', dict()))

    @classmethod
    def from_json_file(cls, json_file):
        """Create EmbedHTMLGenerator object from a .json file.

        :param str json_file: .json file
        :return: new EmbedHTMLGenerator object
        :rtype: EmbedHTMLGenerator
        """
        with open(json_file, 'rb') as f:
            json_dict = json.loads(f.read())
        return cls(json_dict.get('embed', dict()))

    @staticmethod
    def __cleanup(embed_html):
        """Remove <p>...</p> leftover from discord_markdown.convert_to_html().

        :param str embed_html: embed_html string that contains <p></p>
        :return: embed_html string without <p></p>
        """
        # todo: monkey patch discord_markdown to ignore line breaks all together
        embed_html = embed_html.replace('<p>', '')
        embed_html = embed_html.replace('</p>', '\n')
        return embed_html

    def __str__(self):
        """YEP divs. All of this is required for the correct formatting in combination with discord_embed.css"""
        return self.__cleanup(textwrap.dedent(f'''
<div class="flex-vertical whitney theme-dark">
<div class="chat flex-vertical flex-spacer">
<div class="content flex-spacer flex-horizontal">
<div class="flex-spacer flex-vertical messages-wrapper">
<div class="scroller-wrap">
<div class="scroller messages">
<div class="message-group hide-overflow">
<div class="comment">
<div class="message first">
<div class="accessory">

<div class="embed-wrapper">
{self.__color_pill}
<div class="embed embed-rich">
<div class="embed-content">
<div class="embed-content-inner">
{self.__author}
{self.__title}
{self.__description}
{self.__fields}
</div>
{self.__thumbnail}
</div>
{self.__image}
{self.__footer}
</div></div></div></div></div></div></div></div></div></div></div></div>   
            '''))
