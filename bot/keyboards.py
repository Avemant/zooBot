from __future__ import annotations

from urllib.parse import quote

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

from bot import config
from bot.models import AnimalType, Question

PREFIX_ANSWER = "ans:"
ACTION_START = "action:start"
ACTION_HELP = "action:help"
ACTION_ADOPTION = "action:adoption"
ACTION_SHARE = "action:share"
ACTION_CONTACT = "action:contact"
ACTION_FEEDBACK = "action:feedback"
ACTION_RESTART = "action:restart"
FEEDBACK_PREFIX = "fb:"


def answer_callback(answer_id: str) -> str:
    return f"{PREFIX_ANSWER}{answer_id}"


def extract_answer_id(callback_data: str) -> str:
    return callback_data[len(PREFIX_ANSWER) :]


def is_answer_callback(callback_data: str) -> bool:
    return callback_data.startswith(PREFIX_ANSWER)


def is_feedback_rating(callback_data: str) -> bool:
    return callback_data.startswith(FEEDBACK_PREFIX)


def extract_feedback_rating(callback_data: str) -> str:
    return callback_data[len(FEEDBACK_PREFIX) :]


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("🎯 Начать викторину"), KeyboardButton("ℹ️ Помощь")],
        ],
        resize_keyboard=True,
    )


def welcome_inline_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🚀 Начать викторину", callback_data=ACTION_START)],
            [InlineKeyboardButton("📖 Как это работает?", callback_data=ACTION_HELP)],
        ]
    )


def question_keyboard(question: Question) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(option.text, callback_data=answer_callback(option.option_id))]
        for option in question.options
    ]
    return InlineKeyboardMarkup(rows)


def result_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🐾 Узнать об опеке", callback_data=ACTION_ADOPTION),
                InlineKeyboardButton("📣 Поделиться", callback_data=ACTION_SHARE),
            ],
            [
                InlineKeyboardButton("✉️ Связаться с зоопарком", callback_data=ACTION_CONTACT),
                InlineKeyboardButton("⭐ Оставить отзыв", callback_data=ACTION_FEEDBACK),
            ],
            [InlineKeyboardButton("🔄 Попробовать ещё раз?", callback_data=ACTION_RESTART)],
        ]
    )


def feedback_rating_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("⭐", callback_data=f"{FEEDBACK_PREFIX}1"),
                InlineKeyboardButton("⭐⭐", callback_data=f"{FEEDBACK_PREFIX}2"),
                InlineKeyboardButton("⭐⭐⭐", callback_data=f"{FEEDBACK_PREFIX}3"),
                InlineKeyboardButton("⭐⭐⭐⭐", callback_data=f"{FEEDBACK_PREFIX}4"),
                InlineKeyboardButton("⭐⭐⭐⭐⭐", callback_data=f"{FEEDBACK_PREFIX}5"),
            ]
        ]
    )


def build_share_url(animal: AnimalType) -> str:
    text = (
        f"Моё тотемное животное в Московском зоопарке — {animal.display_name}! "
        f"🐾 Пройди викторину: https://t.me/{config.BOT_USERNAME}"
    )
    bot_url = f"https://t.me/{config.BOT_USERNAME}"
    return f"https://t.me/share/url?url={quote(bot_url)}&text={quote(text)}"


def share_keyboard(animal: AnimalType) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("📤 Отправить друзьям", url=build_share_url(animal))]]
    )
