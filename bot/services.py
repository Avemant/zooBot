from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

from bot.config import FEEDBACK_FILE
from bot.models import UserSession

logger = logging.getLogger(__name__)


class SessionManager:
    def __init__(self) -> None:
        self._sessions: Dict[int, UserSession] = {}

    def get_or_create(self, chat_id: int) -> UserSession:
        if chat_id not in self._sessions:
            self._sessions[chat_id] = UserSession()
        return self._sessions[chat_id]

    def remove(self, chat_id: int) -> None:
        self._sessions.pop(chat_id, None)

    @property
    def active_count(self) -> int:
        return len(self._sessions)


class FeedbackService:
    def __init__(self, feedback_path: str | Path | None = None) -> None:
        self._path = Path(feedback_path or FEEDBACK_FILE)

    def save_feedback(
        self,
        user_id: int,
        username: str | None,
        rating: str | None,
        comment: str,
    ) -> None:
        line = (
            f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}] "
            f"userId={user_id} username={self._sanitize(username)} "
            f"rating={self._sanitize(rating)} comment={self._sanitize(comment)}\n"
        )
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with self._path.open("a", encoding="utf-8") as file:
                file.write(line)
            logger.info("Сохранён отзыв от userId=%s", user_id)
        except OSError as exc:
            logger.error("Не удалось сохранить отзыв userId=%s: %s", user_id, exc)

    @staticmethod
    def _sanitize(value: str | None) -> str:
        if not value:
            return "unknown"
        return value.replace("\n", " ").replace("\r", " ").strip()
