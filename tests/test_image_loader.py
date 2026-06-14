from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
from telegram import InputFile

from bot.image_loader import _download_sync, load_photo


def test_download_sync_success():
    fake_data = b"fake-jpeg-data"
    mock_response = MagicMock()
    mock_response.headers.get.return_value = "image/jpeg"
    mock_response.read.return_value = fake_data
    mock_response.__enter__ = lambda s: s
    mock_response.__exit__ = MagicMock(return_value=False)

    with patch("bot.image_loader.urllib.request.urlopen", return_value=mock_response):
        result = _download_sync("https://example.com/photo.jpg")

    assert result == (fake_data, "image/jpeg")


def test_download_sync_returns_none_on_error():
    with patch(
        "bot.image_loader.urllib.request.urlopen",
        side_effect=OSError("network error"),
    ):
        assert _download_sync("https://example.com/photo.jpg") is None


@pytest.mark.asyncio
async def test_load_photo_success():
    fake_data = b"fake-jpeg-data"

    with patch("bot.image_loader._download_sync", return_value=(fake_data, "image/jpeg")):
        result = await load_photo("https://example.com/photo.jpg", "lion")

    assert isinstance(result, InputFile)
    assert result.filename == "lion.jpg"
