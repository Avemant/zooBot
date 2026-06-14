from __future__ import annotations

import logging
import sys
from pathlib import Path

# Позволяет запускать как `python main.py` из папки tgbot_py
sys.path.insert(0, str(Path(__file__).resolve().parent))

from bot import config
from bot.handlers import build_application

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)


def main() -> None:
    errors = config.validate_config()
    if errors:
        for error in errors:
            logging.error(error)
        logging.error(
            "Создайте файл .env в папке tgbot_py (см. .env.example) или задайте переменные окружения."
        )
        sys.exit(1)

    application = build_application()
    logging.info(
        "Бот @%s запущен. Программа «Тотемное животное» готова к работе.",
        config.BOT_USERNAME,
    )
    application.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
