from getpass import getpass

from wcwidth import wcswidth

from core.logger import log


class Prompter:
    def __init__(self, logger):
        self.logger = logger
        self._emoji_width = logger._emoji_width
        self.emoji = logger.EMOJIS["input"]

    def _format_emoji(self, emoji):
        width = wcswidth(emoji)
        padding = max(0, self._emoji_width - width)
        return f"{emoji}{' ' * padding}"

    def ask(self, message, indent=0):
        complete_indent = self.logger.indent_str * (self.logger.indent_level + indent)
        emoji_display = self._format_emoji(self.emoji)
        return input(f"{complete_indent}{emoji_display} {message}: ").strip()

    def ask_password(self, message, indent=0):
        complete_indent = self.logger.indent_str * (self.logger.indent_level + indent)
        return getpass(f"{complete_indent}   {message}: ").strip()

    def ask_yes_no(self, message, indent=0):
        response = self.ask(f"{message} (y/n)", indent)
        return response.lower() == "y"

prompter = Prompter(log)