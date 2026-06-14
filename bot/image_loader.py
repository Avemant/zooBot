from __future__ import annotations

import asyncio
import logging
import urllib.error
import urllib.request
from io import BytesIO

from telegram import InputFile

logger = logging.getLogger(__name__)

BROWSER_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def _download_sync(image_url: str) -> tuple[bytes, str] | None:
    request = urllib.request.Request(
        image_url,
        headers={
            "User-Agent": BROWSER_USER_AGENT,
            "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
            "Referer": "https://commons.wikimedia.org/",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            content_type = response.headers.get("Content-Type", "image/jpeg")
            return response.read(), content_type
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        logger.warning("Не удалось загрузить фото %s: %s", image_url, exc)
        return None


async def load_photo(image_url: str, filename_stem: str) -> InputFile | None:
    """Скачивает изображение и возвращает файл для отправки в Telegram."""
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, _download_sync, image_url)
    if result is None:
        return None

    data, content_type = result
    extension = _extension_from_content_type(content_type)
    return InputFile(BytesIO(data), filename=f"{filename_stem}.{extension}")


def _extension_from_content_type(content_type: str) -> str:
    if "png" in content_type:
        return "png"
    if "webp" in content_type:
        return "webp"
    if "gif" in content_type:
        return "gif"
    return "jpg"
