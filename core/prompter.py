from wcwidth import wcswidth


class Prompter:
    def __init__(self):
        self._emoji_width = 2  
        self.emoji = "➡️ "
    def _format_emoji(self, emoji):
        width = wcswidth(emoji)
        padding = max(0, self._emoji_width - width)
        return f"{emoji}{' ' * padding}"

    def ask(self, message, indent=0):
        complete_indent = "    " * indent
        emoji_display = self._format_emoji(self.emoji)
        return input(f"{complete_indent}{emoji_display} {message}: ").strip()

    def ask_yes_no(self, message, indent=0):
        response = self.ask(f"{message} (y/n)", indent)
        return response.lower() == "y"

prompter = Prompter()