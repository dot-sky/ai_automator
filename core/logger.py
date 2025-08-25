class EmojiLogger:
    EMOJIS = {
        "info": "💬",
        "warning": "⚠️",
        "error": "❌",
        "success": "✅",
        "input": "➡️",
    }

    def info(self, msg):
        print(f"{self.EMOJIS['info']} {msg}")

    def warning(self, msg):
        print(f"{self.EMOJIS['warning']} {msg}")

    def error(self, msg):
        print(f"{self.EMOJIS['error']} {msg}")

    def success(self, msg):
        print(f"{self.EMOJIS['success']} {msg}")

    def input(self, msg):
        print(f"{self.EMOJIS['input']} {msg}")


# global instance
log = EmojiLogger()