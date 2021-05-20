"""
Utility functions that are only really in a separate module to clean up rules.py a bit.
"""
import os
import functools
import re
import pathlib
import logging

import gspread
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
import requests

logger = logging.getLogger('formatter.util')
logger.level = logging.WARN

GS_URL = os.environ.get('GS_URL')
GS_PRIVATE_KEY = os.environ.get('GS_PRIVATE_KEY')
GS_CLIENT_EMAIL = os.environ.get('GS_CLIENT_EMAIL')
GS_TOKEN_URI = os.environ.get('GS_TOKEN_URI')

BASE_DOMAIN = "pvme.github.io"

MODULE_PATH = pathlib.Path(__file__).parent.absolute()


@functools.lru_cache(maxsize=None)
def obtain_pvme_spreadsheet_data(worksheet: str) -> dict:
    """Obtain a worksheet from the PVME-guides price spreadsheet.
    This function is only called once for every worksheet (function caching).

    :param worksheet: Worksheet to obtain (e.g. Perks/Consumables)
    :return: all the worksheet contents as a dictionary or None (cannot obtain the worksheet)
    """
    try:
        # set the credentials
        credentials = ServiceAccountCredentials.from_service_account_info({
            'private_key': GS_PRIVATE_KEY,
            'client_email': GS_CLIENT_EMAIL,
            'token_uri': GS_TOKEN_URI},
            scopes=gspread.auth.READONLY_SCOPES)

        # authenticate + obtain the pvme-guides spreadsheet URL
        gc = gspread.client.Client(auth=credentials)
        sh = gc.open_by_url(GS_URL)

        worksheet = sh.worksheet(worksheet)
    except ValueError as e:
        logger.warning(f"PVME-spreadsheet ValueError: {e}")
    except gspread.exceptions.GSpreadException as e:
        logger.warning(f"PVME-spreadsheet GSpreadException: {e}")
    except Exception as e:
        logger.warning(f"PVME-spreadsheet Exception: {e}")
    else:
        return worksheet.get_all_values()


def generate_embed(url: str) -> str:
    """Obtain the html embed url from a raw (un-parsed) url.
    All common urls are checked for a fixed format in order to greatly reduce build time.
    For other url formats, the metadata is requested after which an embed is generated based on the metadata.

    :param url: raw un-parsed url
    :return: html formatted embed url or None (no embed url is discovered)
    """
    # todo: open graph protocol formatting
    # todo: open graph protocol parsing for unknown urls
    # i.imgur (png) note: can be managed in else but about 90% of the urls are in this format so it speeds up
    if re.match(r"https?://i\.imgur\.com/([a-zA-Z0-9]+)\.png", url):
        embed = "<img class=\"media\" src=\"{}\">".format(url)

    # youtu.be
    elif match := re.match(r"https?://youtu\.be/([a-zA-Z0-9_\-]+)", url):
        embed = "<iframe class=\"media\" width=\"560\" height=\"315\" src=\"https://www.youtube.com/embed/{}\" frameborder=\"0\" allow=\"accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture\" allowfullscreen></iframe>".format(match.group(1))

    # youtube.com
    elif match := re.match(r"https?://(www\.)?youtube\.[a-z0-9.]*?/watch\?([0-9a-zA-Z$\-_.+!*'(),;/?:@=&#]*&)?v=([a-zA-Z0-9_\-]+)", url):
        embed = "<iframe class=\"media\" width=\"560\" height=\"315\" src=\"https://www.youtube.com/embed/{}\" frameborder=\"0\" allow=\"accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture\" allowfullscreen></iframe>".format(match.group(3))

    # clips.twitch.tv
    elif match := re.match(r"https?://clips\.twitch\.tv/([a-zA-Z]+)", url):
        embed = "<iframe class=\"media\" src=\"https://clips.twitch.tv/embed?autoplay=false&clip={}&parent={}\" frameborder=\"0\" allowfullscreen=\"true\" scrolling=\"no\" height=\"315\" width=\"560\"></iframe>".format(match.group(1), BASE_DOMAIN)

    # twitch.tv/videos
    elif match := re.match(r"https?://www\.twitch\.tv/videos/([0-9a-zA-Z]+)", url):
        embed = "<iframe class=\"media\" src=\"https://player.twitch.tv/?autoplay=false&video=v{}&parent={}\" frameborder=\"0\" allowfullscreen=\"true\" scrolling=\"no\" height=\"315\" width=\"560\"></iframe>".format(match.group(1), BASE_DOMAIN)

    # streamable
    elif match := re.match(r"https?://streamable\.com/([a-zA-Z0-9]+)", url):
        embed = "<iframe class=\"media\" src=\"https://streamable.com/o/{}\" frameborder=\"0\" scrolling=\"no\" width=\"560\" height=\"315\" allowfullscreen></iframe>".format(match.group(1))

    # pastebin
    elif match := re.match(r"https?://pastebin.com/([a-zA-Z0-9]+)", url):
        embed = "<iframe class=\"media\" src=\"https://pastebin.com/embed_iframe/{}?theme=dark\" style=\"width:560px;height:155px\"></iframe>".format(match.group(1))

    else:
        # gyazo
        if re.match(r"https?://gyazo\.com/([0-9a-fA-Z]+)", url):
            # todo: fetch api.gyazo.com to obtain the reformatted i.gyazo.com url
            adjusted_url = url

        # gfycat
        elif match := re.match(r"https?://gfycat\.com/([a-zA-Z0-9]+)", url):
            # todo: fetch api.gfycat.com to obtain the reformatted i.gyazo.com url
            adjusted_url = url

        # unknown url
        else:
            adjusted_url = url

        # obtain the type of embed from a request
        if adjusted_url.endswith(".gifv"):
            adjusted_url = re.sub(r"\.gifv$", ".mp4", adjusted_url)

        try:
            response = requests.head(adjusted_url)
            url_type = response.headers.get('content-type', '') if response.status_code == 200 else ''
        except requests.exceptions.RequestException:
            embed = None
        else:
            if url_type.startswith("image/"):
                embed = "<img class=\"media\" src=\"{}\">".format(adjusted_url)
            elif url_type.startswith("video/"):
                embed = "<video class=\"media\" autoplay loop muted controls><source src=\"{}\"></video>".format(adjusted_url)
            else:
                embed = None

    return embed


def parse_channel_id_file() -> dict:
    """Generate a lookup table (dict) with the following content: {channel_id: path_to_channel}.
    The path ignores the '.txt' extension and it does not add a custom extension as this depends on Sphinx/Mkdocs.

    :return: lookup table (dict), when no file is discovered, an empty dict is returned
    """
    channel_id_file = f"{MODULE_PATH}/discord_channels.txt"
    if os.path.exists(channel_id_file):
        with open(channel_id_file, 'r') as file:
            # create dict from regex list of tuples containing group(channel_id), group(path_to_channel)
            channel_lookup = dict(re.findall(r"\| ([0-9]{18}) \| ([-a-z/0-9]+)\.txt", file.read()))
    else:
        channel_lookup = dict()

    return channel_lookup


def parse_user_id_file() -> dict:
    """Generate a lookup table (dict) with the following content: {user_id: user name}.

    :return: lookup table (dict), when no file is discovered, an empty dict is returned
    """
    user_id_file = f"{MODULE_PATH}/discord_users.txt"
    if os.path.exists(user_id_file):
        with open(user_id_file, 'r') as file:
            # create dict from regex list of tuples containing group(user_id), group(user_name)
            # note: parsed as regex since it's not a default json format and I don't want to modify the file.
            user_lookup = dict(re.findall(r"id: '([0-9]{18})', username: '([^']+)'", file.read()))
    else:
        user_lookup = dict()

    return user_lookup


def parse_role_id_file() -> dict:
    """Generate a lookup table (dict) with the following content: {role_id: (channel_name, style)}.

    :return: lookup table (dict), when no file is discovered, an empty dict is returned
    """
    role_id_file = f"{MODULE_PATH}/discord_roles.txt"
    if os.path.exists(role_id_file):
        with open(role_id_file, 'r') as file:
            # create dict from regex list of tuples containing group(role_id): (group(role_name), group(style))
            role_lookup = dict()
            for match in re.finditer(r"([0-9]{18})\|([^|]+)\|([^|]+)\|", file.read()):
                role_lookup[match.group(1)] = (match.group(2), match.group(3))
    else:
        role_lookup = dict()

    return role_lookup

