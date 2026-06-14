import os
from unittest.mock import patch

from bot import config


def test_validate_config_missing_token():
    with patch.dict(os.environ, {"BOT_TOKEN": "", "BOT_USERNAME": ""}, clear=False):
        with patch("bot.config.BOT_TOKEN", ""):
            with patch("bot.config.BOT_USERNAME", ""):
                errors = config.validate_config()
                assert len(errors) == 2


def test_is_admin_configured():
    with patch("bot.config.ADMIN_CHAT_ID", "12345"):
        assert config.is_admin_configured() is True

    with patch("bot.config.ADMIN_CHAT_ID", ""):
        assert config.is_admin_configured() is False
