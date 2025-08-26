from wcwidth import wcswidth


class EmojiLogger:
    EMOJIS = {
        "info": "💬",
        "warning": "⚠️ ",
        "error": "❌",
        "success": "✅",
        "input": "➡️ ",
        "title": "▶️ "
    }

    def __init__(self):
        self.indent_level = 0
        self.indent_str = "    "  # 4 spaces
        self._emoji_width = 2 

    def _print(self, emoji, msg, indent=0):
        complete_indent = self.indent_str * (self.indent_level + indent)
        # actual width of emoji in terminal
        width = wcswidth(emoji)
        padding = max(0, self._emoji_width - width)
        print(f"{complete_indent}{emoji}{' ' * padding} {msg}")

    def title(self, msg):
        self._print(self.EMOJIS["title"], msg)
        self.indent_level += 1

    def end_title(self):
        if self.indent_level > 0:
            self.indent_level -= 1

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
        print(f"{indent}{' ' * self._emoji_width} {msg}")

# Global instance
log = EmojiLogger()
