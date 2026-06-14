from __future__ import annotations

import logging
from pathlib import Path

from dotenv import load_dotenv
import os

logger = logging.getLogger(__name__)

_ENV_CANDIDATES = (Path(".env"), Path("tgbot_py") / ".env")


def _load_dotenv() -> None:
    for path in _ENV_CANDIDATES:
        if path.is_file():
            load_dotenv(path)
            logger.info("Загружен файл конфигурации: %s", path.resolve())
            return
    logger.debug("Файл .env не найден, используются переменные окружения")


_load_dotenv()


def _strip_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def _get(name: str, default: str = "") -> str:
    value = os.getenv(name, default)
    if not value:
        return default
    value = _strip_quotes(value.strip())
    return value if value else default


BOT_TOKEN: str = _get("BOT_TOKEN")
BOT_USERNAME: str = _get("BOT_USERNAME")
ADMIN_CHAT_ID: str = _get("ADMIN_CHAT_ID")
CONTACT_EMAIL: str = _get("CONTACT_EMAIL", "opека@moscowzoo.ru")
FEEDBACK_FILE: str = _get("FEEDBACK_FILE", "feedback.log")
ZOO_ADOPTION_URL = "https://moscowzoo.ru/oplata/oplata-opieki/"
ZOO_CHANNEL_URL = "https://t.me/moscowzoo_official"


def is_admin_configured() -> bool:
    return bool(ADMIN_CHAT_ID)


def validate_config() -> list[str]:
    errors: list[str] = []
    if not BOT_TOKEN:
        errors.append("BOT_TOKEN не задан (укажите в .env или переменных окружения)")
    if not BOT_USERNAME:
        errors.append("BOT_USERNAME не задан (имя бота без @)")
    return errors
