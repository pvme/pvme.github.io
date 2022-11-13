from typing import List, Union, Tuple


class NavStructure(dict):
    def __setitem__(self, keys: List[str], value: Union[Tuple[str, str], str]):
        cur = self
        for key in keys:
            cur = cur.setdefault(key, {})
        cur[value[0]] = value[1]


class NavInterface:
    def __init__(self, mkdocs_nav):
        self.__nav = mkdocs_nav
        self.__structure = NavStructure()

    def add_item(self, category_name, forum_name, channel_name, output_file):
        keys = [category_name]
        if forum_name:
            keys.append(forum_name)
        self.__structure[keys] = channel_name, output_file

    def update_mkdocs_nav(self):
        self.__nav.extend([{key: value} for key, value in self.__structure.items()])
