from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class AnimalType(Enum):
    ELEPHANT = (
        "слон",
        "Слон",
        "Мудрый и общительный — как слон из Московского зоопарка!\n"
        "Слоны помнят друзей годами, любят водные процедуры и умеют работать в команде.\n"
        "Твоё тотемное животное — настоящий лидер стада с добрым сердцем.",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/37/African_Bush_Elephant.jpg/960px-African_Bush_Elephant.jpg",
    )
    LION = (
        "лев",
        "Лев",
        "Царственный и уверенный — ты настоящий лев!\n"
        "Львы в зоопарке ценят отдых после активного дня и умеют заботиться о своей прайде.\n"
        "Твоё тотемное животное — символ силы и благородства.",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/73/Lion_waiting_in_Namibia.jpg/960px-Lion_waiting_in_Namibia.jpg",
    )
    MEERKAT = (
        "сурикат",
        "Сурикат",
        "Бдительный и любопытный — ты сурикат!\n"
        "Сурикаты в зоопарке всегда на страже: один дозорный, остальные — за делом.\n"
        "Твоё тотемное животное — душа компании и главный «наблюдатель».",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Meerkat_%28Suricata_suricatta%29_Tswalu.jpg/960px-Meerkat_%28Suricata_suricatta%29_Tswalu.jpg",
    )
    FLAMINGO = (
        "фламинго",
        "Фламинго",
        "Изящный и общительный — ты фламинго!\n"
        "Розовый цвет фламинго — от любимой еды (водоросли и рачки), а не от моды.\n"
        "Твоё тотемное животное — грация и умение быть в центре внимания.",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3b/Greater_Flamingo_%28Phoenicopterus_roseus%29%2C_Lake_Nakuru%2C_Kenya.jpg/960px-Greater_Flamingo_%28Phoenicopterus_roseus%29%2C_Lake_Nakuru%2C_Kenya.jpg",
    )
    PORCUPINE = (
        "дикобраз",
        "Дикобраз",
        "Да ты дикобраз! Независимый, с характером и мягким сердцем внутри.\n"
        "Дикобразы в зоопарке — мастера самообороны, но очень дружелюбны к тем, кого знают.\n"
        "Твоё тотемное животное — ценит личное пространство и настоящую дружбу.",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Crested_Porcupine_%28Hystrix_cristata%29.jpg/960px-Crested_Porcupine_%28Hystrix_cristata%29.jpg",
    )
    PRZEWALSKI_HORSE = (
        "лошадь Пржевальского",
        "Лошадь Пржевальского",
        "Дух свободы — ты лошадь Пржевальского!\n"
        "Этот вид исчез в дикой природе и сохранился благодаря зоопаркам мира, включая Московский.\n"
        "Твоё тотемное животное — символ сохранения биоразнообразия.",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/Przewalski%27s_Horse.jpg/960px-Przewalski%27s_Horse.jpg",
    )
    BEAR = (
        "медведь",
        "Медведь",
        "Сильный и основательный — ты медведь!\n"
        "Медведи любят комфорт, хорошую еду и уютный сон после насыщенного дня.\n"
        "Твоё тотемное животное — надёжный друг с мягкой душой.",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/71/2010-kodiak-bear-1.jpg/960px-2010-kodiak-bear-1.jpg",
    )
    GIRAFFE = (
        "жираф",
        "Жираф",
        "Смотришь на мир с высоты — ты жираф!\n"
        "Жирафы в зоопарке покоряют ростом и спокойным характером.\n"
        "Твоё тотемное животное — умеет видеть перспективу и оставаться уравновешенным.",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Giraffe_Mikumi_National_Park.jpg/960px-Giraffe_Mikumi_National_Park.jpg",
    )

    def __init__(self, animal_id: str, display_name: str, description: str, image_url: str) -> None:
        self.animal_id = animal_id
        self.display_name = display_name
        self.description = description
        self.image_url = image_url


class SessionState(str, Enum):
    IDLE = "idle"
    QUIZ_IN_PROGRESS = "quiz"
    AWAITING_FEEDBACK = "feedback"
    AWAITING_CONTACT = "contact"


@dataclass
class AnswerOption:
    option_id: str
    text: str
    animal_scores: Dict[AnimalType, int]


@dataclass
class Question:
    question_id: str
    text: str
    options: List[AnswerOption]


@dataclass
class UserSession:
    state: SessionState = SessionState.IDLE
    current_question_index: int = 0
    selected_answer_ids: List[str] = field(default_factory=list)
    result_animal: Optional[AnimalType] = None
    pending_feedback_rating: Optional[str] = None

    def reset_quiz(self) -> None:
        self.state = SessionState.QUIZ_IN_PROGRESS
        self.current_question_index = 0
        self.selected_answer_ids.clear()
        self.result_animal = None
        self.pending_feedback_rating = None

    def reset_to_idle(self) -> None:
        self.state = SessionState.IDLE
        self.current_question_index = 0
        self.selected_answer_ids.clear()
        self.result_animal = None
        self.pending_feedback_rating = None
