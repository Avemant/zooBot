from __future__ import annotations

from typing import Dict, List, Optional

from bot.models import AnimalType, AnswerOption, Question


def _scores(**kwargs: int) -> Dict[AnimalType, int]:
    return {AnimalType[k]: v for k, v in kwargs.items()}


def _option(option_id: str, text: str, scores: Dict[AnimalType, int]) -> AnswerOption:
    return AnswerOption(option_id, text, scores)


QUESTIONS: List[Question] = [
    Question(
        "weekend",
        "Как вы проводите идеальный выходной?",
        [
            _option(
                "weekend_team",
                "С семьёй и друзьями — чем больше, тем веселее",
                _scores(ELEPHANT=3, MEERKAT=2, FLAMINGO=2),
            ),
            _option(
                "weekend_solo",
                "Наедине с природой или книгой",
                _scores(BEAR=3, PORCUPINE=2, PRZEWALSKI_HORSE=2),
            ),
            _option(
                "weekend_active",
                "Активно: прогулки, спорт, приключения",
                _scores(LION=3, GIRAFFE=2, PRZEWALSKI_HORSE=1),
            ),
            _option(
                "weekend_cozy",
                "Дома, в уюте, с вкусной едой",
                _scores(BEAR=2, PORCUPINE=2, ELEPHANT=1),
            ),
        ],
    ),
    Question(
        "friends",
        "Как друзья обычно описывают вас?",
        [
            _option("friends_leader", "Лидер и защитник", _scores(LION=3, ELEPHANT=2)),
            _option("friends_watcher", "Бдительный и внимательный", _scores(MEERKAT=3, GIRAFFE=1)),
            _option("friends_elegant", "Стильный и харизматичный", _scores(FLAMINGO=3, GIRAFFE=2)),
            _option(
                "friends_unique",
                "Особенный, со своим характером",
                _scores(PORCUPINE=3, PRZEWALSKI_HORSE=2),
            ),
        ],
    ),
    Question(
        "food",
        "Какая еда вам ближе?",
        [
            _option(
                "food_veggie",
                "Овощи, фрукты, зелень",
                _scores(GIRAFFE=3, ELEPHANT=2, FLAMINGO=1),
            ),
            _option("food_meat", "Сытное и белковое", _scores(LION=3, BEAR=2)),
            _option(
                "food_varied",
                "Всё понемногу — главное разнообразие",
                _scores(MEERKAT=2, ELEPHANT=2, FLAMINGO=1),
            ),
            _option("food_sweet", "Сладкое и уютное (мёд, десерты)", _scores(BEAR=3, PORCUPINE=1)),
        ],
    ),
    Question(
        "surprise",
        "Что делаете, когда случается неожиданность?",
        [
            _option("surprise_calm", "Спокойно оцениваю ситуацию", _scores(GIRAFFE=3, ELEPHANT=2)),
            _option(
                "surprise_alert",
                "Мгновенно включаю «режим дозора»",
                _scores(MEERKAT=3, PORCUPINE=1),
            ),
            _option(
                "surprise_action",
                "Действую решительно",
                _scores(LION=3, PRZEWALSKI_HORSE=2),
            ),
            _option(
                "surprise_retreat",
                "Отхожу в сторону и обдумываю",
                _scores(PORCUPINE=3, BEAR=2),
            ),
        ],
    ),
    Question(
        "habitat",
        "Где бы вы хотели жить?",
        [
            _option(
                "habitat_savanna",
                "В просторной саванне под открытым небом",
                _scores(LION=2, GIRAFFE=2, ELEPHANT=2),
            ),
            _option(
                "habitat_water",
                "У воды — река, озеро или море",
                _scores(FLAMINGO=3, ELEPHANT=2),
            ),
            _option(
                "habitat_mountains",
                "В горах или степи, где простор и свобода",
                _scores(PRZEWALSKI_HORSE=3, BEAR=2),
            ),
            _option(
                "habitat_burrow",
                "В уютном укрытии, но с выходом «в свет»",
                _scores(MEERKAT=2, PORCUPINE=3, BEAR=1),
            ),
        ],
    ),
    Question(
        "morning",
        "Вы — «жаворонок» или «сова»?",
        [
            _option("morning_early", "Встаю рано и сразу в дело", _scores(MEERKAT=3, LION=1)),
            _option("morning_late", "Люблю поспать подольше", _scores(BEAR=3, LION=2)),
            _option("morning_social", "Утро — время для общения", _scores(FLAMINGO=3, ELEPHANT=2)),
            _option(
                "morning_quiet",
                "Утро — тихий час для себя",
                _scores(PORCUPINE=2, GIRAFFE=2, PRZEWALSKI_HORSE=1),
            ),
        ],
    ),
]


def get_question_count() -> int:
    return len(QUESTIONS)


def get_question(index: int) -> Question:
    return QUESTIONS[index]


def find_answer(answer_id: str) -> Optional[AnswerOption]:
    for question in QUESTIONS:
        for option in question.options:
            if option.option_id == answer_id:
                return option
    return None
