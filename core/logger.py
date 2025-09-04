import os

from wcwidth import wcswidth


class EmojiLogger:
    EMOJIS = {
        "info": "💬",
        "warning": "⚠️ ",
        "error": "❌",
        "success": "✅",
        "input": "📝",
        "title": "✨ "
    }

    def __init__(self):
        self.indent_level = 0
        self.indent_str = "    "  
        self._emoji_width = 2 

    def _print(self, emoji, msg, indent=0):
        complete_indent = self.indent_str * (self.indent_level + indent)
        width = wcswidth(emoji)
        padding = max(0, self._emoji_width - width)
        print(f"{complete_indent}{emoji}{' ' * padding} {msg}")

    def indent(self):
        self.indent_level += 1

    def dedent(self):
        if self.indent_level > 0:
            self.indent_level -= 1

    def title(self, msg):
        border = "─" * (len(msg) + 6)
        print()  
        print(border)
        self._print(self.EMOJIS["title"], msg)
        print(border)
        self.indent()

    def end_title(self):
        self.dedent()

    def info(self, msg, indent=0):
        self._print(self.EMOJIS["info"], msg, indent)

    def warning(self, msg, indent=0):
        self._print(self.EMOJIS["warning"], msg, indent)

    def error(self, msg, indent=0):
        self._print(self.EMOJIS["error"], msg, indent)

    def success(self, msg, indent=0):
        self._print(self.EMOJIS["success"], msg, indent)

    def input(self, msg, indent=0):
        self._print(self.EMOJIS["input"], msg, indent)

    def plain(self, msg, indent=0):
        indent = self.indent_str * (self.indent_level + indent)
        print(f"{indent} {msg}")

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')
# Global instance
log = EmojiLogger()
