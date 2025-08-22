import logging
import sys

EMOJIS = {
    "info": "💬",
    "warn": "⚠️",
    "success": "✅",
    "input": "➡️",
    "error": "❌",
}

class EmojiFormatter(logging.Formatter):
    def format(self, record):
        emoji = EMOJIS.get(record.levelname.lower(), "")
        return f"{emoji} {record.getMessage()}"

def get_logger(name="automation"):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(EmojiFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

log = get_logger()