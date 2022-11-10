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

    def __call__(self, name):
        if name in self.__aliases:
            self.__used_names.add(name)
            name = self.__aliases[name]
        return name

    def __del__(self):
        unused_aliases = '\n- '.join(name for name in self.__aliases.keys() if name not in self.__used_names)
        if len(unused_aliases) > 0:
            logger.warning(f"unused aliases for {self.__name}:\n- {unused_aliases}")


class NameConverter:
    def __init__(self, settings: NameConvertSettings, source_dir: Path):
        self.__category_alias = AliasStore('category', settings.category)
        self.__forum_alias = AliasStore('forum', settings.forum)
        self.__word_alias = AliasStore('word', settings.word)
        self.__channel_alias = {source_dir / channel['path']: channel['name'] for channel in
                                DiscordChannelID.CHANNEL_LOOKUP.values()}

    def channel(self, source_file: Path):
        # __custom_channels.get(source_file, source_file.stem).replace('-', ' ').capitalize()
        name = self.__channel_alias.get(source_file, source_file.stem)
        return self.__format_name(name)

    def forum(self, name):
        name = self.__forum_alias(name.lower())
        return self.__format_name(name)

    def category(self, name):
        name = self.__category_alias(name.lower())
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
            if (custom_word := self.__word_alias(word)) != word:
                words.append(custom_word)
            else:
                # .upper() instead of capitalize() because the latter can remove existing capitalization
                words.append(word[0].upper() + word[1:])
        return ' '.join(words)
