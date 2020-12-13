"""
Utility functions that are only really in a separate module to clean up rules.py a bit.
"""
import os
import functools
import re

import gspread
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
import requests

GS_URL = os.environ.get('GS_URL')
GS_PRIVATE_KEY = os.environ.get('GS_PRIVATE_KEY')
GS_CLIENT_EMAIL = os.environ.get('GS_CLIENT_EMAIL')
GS_TOKEN_URI = os.environ.get('GS_TOKEN_URI')

BASE_DOMAIN = "pvme.github.io"


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
        print("cred done")
        # authenticate + obtain the pvme-guides spreadsheet URL
        gc = gspread.client.Client(auth=credentials)
        print("client done")
        sh = gc.open_by_url(GS_URL)
        print("url done")
        worksheet = sh.worksheet(worksheet)
        print("worksheet")
    except ValueError as e:
        print("ValueError: {}".format(e))
    except gspread.exceptions.APIError as e:
        print("APIError: {}".format(e))
    except Exception as e:
        print("Exception: {}".format(e))
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
