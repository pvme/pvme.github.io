"""
Utility functions that are only really in a separate module to clean up rules.py a bit.
"""
import re
import logging

import requests


logger = logging.getLogger('file_formatter.util')
logger.level = logging.WARN

BASE_DOMAIN = "https://pvme.io"


def get_attachment_from_url(url: str) -> str:
    """Obtain the html embed url from a raw (un-parsed) url.
    All common urls are checked for a fixed format in order to greatly reduce build time.
    For other url formats, the metadata is requested after which an embed is generated based on the metadata.

    :param url: raw un-parsed url
    :return: html formatted embed url or None (no embed url is discovered)
    """
    # todo: open graph protocol formatting
    # todo: open graph protocol parsing for unknown urls
    # todo: warning for None urls
    # todo: https://youtube.com/clip/UgkxHyqloWFPpDtOQVisyq-p-J8GyoFG7i91 (rs3-full-boss-guides\tzkal-zuk\hard-mode.txt)
    # (i.)imgur (png) note: can be managed in else but about 90% of the urls are in this format so it speeds up
    if re.match(r"https?://i?\.?imgur\.com/([a-zA-Z0-9]+)\.png", url):
        embed = "<img class=\"media\" src=\"{}\">".format(url)

    elif re.match(r"https?://i?\.?imgur\.com/([a-zA-Z0-9]+)\.jpe?g", url):
        embed = "<img class=\"media\" src=\"{}\">".format(url)

    # img.pvme.io links
    elif re.match(r"https?://img\.pvme\.io/images/([a-zA-Z0-9]+)\.jpe?g", url):
        embed = "<img class=\"media\" src=\"{}\">".format(url)

    elif re.match(r"https?://img\.pvme\.io/images/([a-zA-Z0-9]+)\.png", url):
        embed = "<img class=\"media\" src=\"{}\">".format(url)

    elif re.match(r"https?://img\.pvme\.io/images/([a-zA-Z0-9]+)\.gif", url):
        embed = "<img class=\"media\" src=\"{}\">".format(url)

    elif re.match(r"https?://img\.pvme\.io/images/([a-zA-Z0-9]+)\.mp4", url):
        embed = "<video class=\"media\" loop muted controls><source src=\"{}\"></video>".format(url)

    elif re.match(r"https?://i?\.?imgur\.com/([a-zA-Z0-9]+)\.mp4", url):
        embed = "<video class=\"media\" loop muted controls><source src=\"{}\" type=\"video/mp4\"></video>".format(url)

    elif re.match(r"https?://i?\.?imgur\.com/([a-zA-Z0-9]+)\.gifv", url):
        adjusted_url = re.sub(r"\.gifv$", ".mp4", url)
        embed = "<video class=\"media\" loop muted controls><source src=\"{}\"></video>".format(adjusted_url)

    # note: not sure if every gif should be formatted as <img/>
    # elif re.match(r"https?://i?\.?imgur\.com/([a-zA-Z0-9]+)\.gif", url):
    #     embed = "<img class=\"media\" src=\"{}\">".format(url)

    # youtu.be
    elif match := re.match(r"https?://youtu\.be/([a-zA-Z0-9_\-]+)", url):
        embed = "<iframe class=\"media\" width=\"560\" height=\"315\" src=\"https://www.youtube.com/embed/{}\" frameborder=\"0\" allow=\"accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture\" allowfullscreen></iframe>".format(match.group(1))

    # youtube.com/watch
    elif match := re.match(r"https?://(www\.)?youtube\.[a-z0-9.]*?/watch\?([0-9a-zA-Z$\-_.+!*'(),;/?:@=&#]*&)?v=([a-zA-Z0-9_\-]+)", url):
        embed = "<iframe class=\"media\" width=\"560\" height=\"315\" src=\"https://www.youtube.com/embed/{}\" frameborder=\"0\" allow=\"accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture\" allowfullscreen></iframe>".format(match.group(3))

    # youtube.com/live
    elif match := re.match(r"https?://(www\.)?youtube\.[a-z0-9.]*?/live/([a-zA-Z0-9_\-]+)", url):
        embed = "<iframe class=\"media\" width=\"560\" height=\"315\" src=\"https://www.youtube.com/embed/{}\" frameborder=\"0\" allow=\"accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture\" allowfullscreen></iframe>".format(match.group(2))

    # youtube.com/clip
    # todo: commented because the only clips currently used are not available, uncomment when/if more clips are used
    # elif match := re.match(r"https?://(www\.)?youtube\.[a-z0-9.]*?/clip/([a-zA-Z0-9_\-]+)", url):
    #     embed = "<iframe class=\"media\" width=\"560\" height=\"315\" src=\"https://www.youtube.com/embed/{}\" frameborder=\"0\" allow=\"accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture\" allowfullscreen></iframe>".format(match.group(2))

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

    # gfycat
    elif re.match(r"https?://([a-zA-Z0-9-]+)\.gfycat\.com/([a-zA-Z0-9-]+)\.mp4", url):
        embed = "<video class=\"media\" loop muted controls><source src=\"{}\"></video>".format(url)

    # i.gyazo.com
    elif re.match(r"https?://i\.gyazo\.com/([a-zA-Z0-9-]+)\.mp4", url):
        embed = "<video class=\"media\" loop muted controls><source src=\"{}\" type=\"video/mp4\"></video>".format(url)

    # discord invite
    elif re.match(r"https?://discord\.gg/([a-zA-Z0-9]{7})", url):
        logger.warning(f'not rendered url: {url}')
        embed = None

    # discord channel
    elif re.match(r"https?://discord\.com/channels/[0-9]{18}/[0-9]{18}/[0-9]{18}", url):
        logger.warning(f'not rendered url: {url}')
        embed = None

    # discord image
    elif re.match(r"https?://media\.discordapp\.net/attachments/[0-9]{18}/[0-9]{18}/([a-zA-Z0-9-]+)\.png", url):
        embed = "<img class=\"media\" src=\"{}\">".format(url)

    else:
        embed = request_embed_from_url(url)

    return embed


def request_embed_from_url(url: str) -> str:
    # obtain the type of embed from a request
    if url.endswith(".gifv"):
        url = re.sub(r"\.gifv$", ".mp4", url)

    try:
        logger.info(f'request url: {url}')
        response = requests.head(url)
        url_type = response.headers.get('content-type', '') if response.status_code == 200 else ''
    except requests.exceptions.RequestException:
        embed = None
    else:
        if url_type.startswith("image/"):
            embed = "<img class=\"media\" src=\"{}\">".format(url)
        elif url_type.startswith("video/"):
            embed = "<video class=\"media\" loop muted controls><source src=\"{}\"></video>".format(url)
        else:
            logger.warning(f'not rendered url: {url}')
            embed = None

    return embed
