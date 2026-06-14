from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from telegram.error import BadRequest

from bot import config, keyboards, messages
from bot.image_loader import load_photo
from bot.models import SessionState
from bot.quiz_data import get_question, get_question_count
from bot.quiz_scoring import calculate_result
from bot.services import FeedbackService, SessionManager

logger = logging.getLogger(__name__)

session_manager = SessionManager()
feedback_service = FeedbackService()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    first_name = user.first_name if user else None
    await update.message.reply_text(
        messages.welcome_message(first_name),
        reply_markup=keyboards.welcome_inline_keyboard(),
    )
    await update.message.reply_text(
        "Или используйте меню ниже 👇",
        reply_markup=keyboards.main_menu_keyboard(),
    )


async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _start_quiz(update)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        messages.help_message(),
        reply_markup=keyboards.main_menu_keyboard(),
    )


async def privacy_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        messages.privacy_message(),
        reply_markup=keyboards.main_menu_keyboard(),
    )


async def text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return

    chat_id = update.effective_chat.id
    text = update.message.text.strip()
    session = session_manager.get_or_create(chat_id)

    if session.state == SessionState.AWAITING_FEEDBACK:
        await _handle_feedback_comment(update, session)
        return
    if session.state == SessionState.AWAITING_CONTACT:
        await _handle_contact_message(update, session)
        return

    if text in ("/quiz", "🎯 Начать викторину"):
        await _start_quiz(update)
    elif text in ("/help", "ℹ️ Помощь"):
        await help_command(update, context)
    else:
        await update.message.reply_text(
            messages.unknown_input(),
            reply_markup=keyboards.main_menu_keyboard(),
        )


async def callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.data:
        return

    await query.answer()
    chat_id = update.effective_chat.id
    session = session_manager.get_or_create(chat_id)
    data = query.data

    if keyboards.is_answer_callback(data):
        if session.state != SessionState.QUIZ_IN_PROGRESS:
            await query.message.reply_text(
                "Викторина не активна. Нажмите «Попробовать ещё раз?» или /quiz"
            )
            return
        await _process_answer(query, session, keyboards.extract_answer_id(data))
        return

    if keyboards.is_feedback_rating(data):
        session.pending_feedback_rating = keyboards.extract_feedback_rating(data)
        session.state = SessionState.AWAITING_FEEDBACK
        await query.message.reply_text(
            "Спасибо! Напишите комментарий одним сообщением или «-», чтобы пропустить."
        )
        return

    if data == keyboards.ACTION_START:
        await _start_quiz(update, from_callback=True)
    elif data == keyboards.ACTION_HELP:
        await query.message.reply_text(messages.help_message())
    elif data == keyboards.ACTION_ADOPTION:
        await query.message.reply_text(messages.adoption_info())
    elif data == keyboards.ACTION_SHARE:
        await _send_share(query.message, session)
    elif data == keyboards.ACTION_CONTACT:
        await _request_contact(query.message, session)
    elif data == keyboards.ACTION_FEEDBACK:
        await query.message.reply_text(
            messages.feedback_prompt(),
            reply_markup=keyboards.feedback_rating_keyboard(),
        )
    elif data == keyboards.ACTION_RESTART:
        await _restart_quiz(query.message, session)
    else:
        logger.warning("Неизвестный callback: %s", data)


async def _start_quiz(update: Update, from_callback: bool = False) -> None:
    chat_id = update.effective_chat.id
    session = session_manager.get_or_create(chat_id)
    session.reset_quiz()

    index = session.current_question_index
    question = get_question(index)
    total = get_question_count()
    text = messages.question_progress(index + 1, total, question.text)
    markup = keyboards.question_keyboard(question)

    if from_callback and update.callback_query and update.callback_query.message:
        await update.callback_query.message.reply_text(text, reply_markup=markup)
    elif update.message:
        await update.message.reply_text(text, reply_markup=markup)


async def _restart_quiz(message, session) -> None:
    session.reset_quiz()
    await message.reply_text(messages.quiz_restarted())

    index = session.current_question_index
    question = get_question(index)
    total = get_question_count()
    await message.reply_text(
        messages.question_progress(index + 1, total, question.text),
        reply_markup=keyboards.question_keyboard(question),
    )


async def _process_answer(query, session, answer_id: str) -> None:
    session.selected_answer_ids.append(answer_id)
    session.current_question_index += 1

    if session.current_question_index >= get_question_count():
        await _finish_quiz(query.message, session)
    else:
        index = session.current_question_index
        question = get_question(index)
        total = get_question_count()
        await query.edit_message_text(
            messages.question_progress(index + 1, total, question.text),
            reply_markup=keyboards.question_keyboard(question),
        )


async def _finish_quiz(message, session) -> None:
    animal = calculate_result(session)
    session.result_animal = animal
    session.state = SessionState.IDLE

    caption = messages.result_caption(animal)
    markup = keyboards.result_keyboard()
    await _send_result_photo(message, animal, caption, markup)

    logger.info(
        "Пользователь chatId=%s получил результат: %s",
        message.chat_id,
        animal.display_name,
    )


async def _send_result_photo(message, animal, caption, markup) -> None:
    # 1. Как в Java — Telegram сам загружает фото по URL
    try:
        await message.reply_photo(
            photo=animal.image_url,
            caption=caption,
            reply_markup=markup,
        )
        return
    except BadRequest as exc:
        logger.warning("Telegram не смог загрузить фото по URL: %s", exc)

    # 2. Скачиваем сами (urllib) и отправляем файлом
    photo = await load_photo(animal.image_url, animal.name.lower())
    if photo:
        await message.reply_photo(photo=photo, caption=caption, reply_markup=markup)
        return

    # 3. Только текст
    await message.reply_text(caption, reply_markup=markup)


async def _send_share(message, session) -> None:
    animal = session.result_animal
    if animal is None:
        await message.reply_text("Сначала пройдите викторину, чтобы поделиться результатом.")
        return
    await message.reply_text(
        messages.share_instructions(animal),
        reply_markup=keyboards.share_keyboard(animal),
    )


async def _request_contact(message, session) -> None:
    if session.result_animal is None:
        await message.reply_text(
            "Сначала пройдите викторину — так сотрудник увидит ваш результат."
        )
        return
    session.state = SessionState.AWAITING_CONTACT
    await message.reply_text(messages.contact_prompt())


async def _handle_contact_message(update: Update, session) -> None:
    message = update.message
    chat_id = update.effective_chat.id
    user_text = message.text.strip()
    session.state = SessionState.IDLE

    if not config.is_admin_configured():
        await message.reply_text(messages.contact_unavailable())
        return

    user = update.effective_user
    username = user.username if user else "unknown"
    animal = session.result_animal
    admin_text = (
        "📩 Новое обращение из бота «Тотемное животное»\n\n"
        f"Пользователь: {user.first_name if user else '—'} "
        f"(@{username or '—'}, id={user.id if user else 0})\n"
        f"Результат викторины: {animal.display_name if animal else 'не пройдена'}\n\n"
        f"Сообщение:\n{user_text}"
    )
    await message.get_bot().send_message(chat_id=config.ADMIN_CHAT_ID, text=admin_text)
    await message.reply_text(messages.contact_sent())
    logger.info("Переслано обращение от chatId=%s админу", chat_id)


async def _handle_feedback_comment(update: Update, session) -> None:
    message = update.message
    comment = message.text.strip()
    if comment == "-":
        comment = ""

    user = update.effective_user
    feedback_service.save_feedback(
        user_id=user.id if user else message.chat_id,
        username=user.username if user else None,
        rating=session.pending_feedback_rating,
        comment=comment,
    )
    session.state = SessionState.IDLE
    session.pending_feedback_rating = None
    await message.reply_text(
        messages.feedback_thanks(),
        reply_markup=keyboards.main_menu_keyboard(),
    )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Ошибка обработки update", exc_info=context.error)
    if isinstance(update, Update) and update.effective_chat:
        try:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Произошла ошибка. Попробуйте ещё раз или отправьте /help.",
            )
        except Exception:
            logger.exception("Не удалось отправить сообщение об ошибке")


def build_application() -> Application:
    application = Application.builder().token(config.BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("quiz", quiz_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("privacy", privacy_command))
    application.add_handler(CallbackQueryHandler(callback_query))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message))
    application.add_error_handler(error_handler)

    return application
