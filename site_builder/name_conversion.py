import logging
from pathlib import Path
import re

from site_builder.structure_settings import NameConvertSettings
from site_builder.formatter.rules import DiscordChannelID


logger = logging.getLogger(__name__)


class AliasStore:
    def __init__(self, name, aliases):
        self.__name = name
        self.__aliases = aliases
        self.__used_names = set()

    def __call__(self, name, no_result_value=None):
        if name in self.__aliases:
            self.__used_names.add(name)
        return self.__aliases.get(name, no_result_value)

    def __del__(self):
        unused_aliases = '\n- '.join(name for name in self.__aliases.keys() if name not in self.__used_names)
        if len(unused_aliases) > 0:
            logger.warning(f"unused aliases for '{self.__name}':\n- {unused_aliases}")


class NameConverter:
    def __init__(self, settings: NameConvertSettings, source_dir: Path):
        self.__category_settings = AliasStore('category', settings.category)
        self.__forum_alias = AliasStore('forum', settings.forum)
        self.__word_alias = AliasStore('word', settings.word)
        self.__channel_alias = {source_dir / channel['path']: channel['name'] for channel in
                                DiscordChannelID.CHANNEL_LOOKUP.values() if channel['path'] not in (None, ' ')}
        self.__extra_channel_alias = AliasStore('extra-channel-alias', settings.extra_channel)

    def channel(self, source_file: Path):
        # __custom_channels.get(source_file, source_file.stem).replace('-', ' ').capitalize()
        name = self.__channel_alias.get(source_file, source_file.stem)
        name = self.__extra_channel_alias(name, name)
        return self.__format_name(name)

    def forum(self, name):
        name = self.__forum_alias(name.lower(), name)
        return self.__format_name(name)

    def category(self, name):
        settings = self.__category_settings(name.lower())
        if settings:
            name = self.__format_name(settings.alias if settings.alias else name)
            if settings.emoji:
                name += f" <img class='nav-emoji' src='https://cdn.discordapp.com/emojis/{settings.emoji}.png?v=1'>"
            return name
        else:
            return self.__format_name(name)

    def __format_name(self, name):
        name = self.__remove_separation_chars(name)
        name = self.__capitalize_words(name)
        return name

    def __remove_separation_chars(self, name):
        return re.sub(r"[-_]", ' ', name)

    def __capitalize_words(self, name):
        words = []
        for word in name.split():
            if custom_word := self.__word_alias(word):
                words.append(custom_word)
            else:
                # .upper() instead of capitalize() because the latter can remove existing capitalization
                words.append(word[0].upper() + word[1:])
        return ' '.join(words)
