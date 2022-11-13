from dataclasses import dataclass
from typing import List, Iterator


@dataclass
class RawMessage:
    """Raw messages split by bot command that are parsed directly from a guide.txt."""
    content: str = None
    bot_command: str = None

    @classmethod
    def from_message_lines(cls, message_lines: list, bot_command: str):
        if len(message_lines) == 0:
            # work-around to avoid unnecessary empty lines
            return cls(bot_command=bot_command)
        return cls('\n'.join(message_lines), bot_command)


class RawMessageParser:
    """Obtains all messages from the contents of a guide"""
    def __init__(self, text: str):
        self.__text: str = text
        self.__raw_messages: List = []

    @property
    def raw_messages(self):
        return self.__raw_messages

    @staticmethod
    def line_is_bot_command(line: str) -> bool:
        return line.startswith('.') and not line.startswith('..')

    @staticmethod
    def message_is_toc(message_lines: List[str]) -> bool:
        return len(message_lines) >= 3 and 'table of contents' in message_lines[2].lower()

    def parse(self):
        message_lines = []

        # for line in self.__text.split('\n'):
        for line in self.__text.splitlines():
            if self.line_is_bot_command(line):
                if not self.message_is_toc(message_lines):
                    self.__raw_messages.append(RawMessage.from_message_lines(message_lines, line))

                message_lines = []
            else:
                message_lines.append(line)

        if len(message_lines) > 0:
            # add last message if it's not closed by a bot command
            self.__raw_messages.append(RawMessage.from_message_lines(message_lines, '.'))


def get_raw_messages(text: str) -> Iterator[RawMessage]:
    message_parser = RawMessageParser(text)
    message_parser.parse()
    for message in message_parser.raw_messages:
        yield message
