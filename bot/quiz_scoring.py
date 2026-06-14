from __future__ import annotations

import logging
from typing import Dict, List

from bot.models import AnimalType, UserSession
from bot.quiz_data import find_answer

logger = logging.getLogger(__name__)


def calculate_result(session: UserSession) -> AnimalType:
    totals: Dict[AnimalType, int] = {animal: 0 for animal in AnimalType}

    for answer_id in session.selected_answer_ids:
        option = find_answer(answer_id)
        if option is None:
            logger.warning("Неизвестный ответ викторины: %s", answer_id)
            continue
        for animal, points in option.animal_scores.items():
            totals[animal] = totals.get(animal, 0) + points

    winner = max(totals, key=lambda animal: (totals[animal], animal.name))
    logger.debug("Результат викторины: %s (баллы: %s)", winner.display_name, totals)
    return winner


def preview_scores(answer_ids: List[str]) -> Dict[AnimalType, int]:
    session = UserSession()
    session.selected_answer_ids.extend(answer_ids)
    totals: Dict[AnimalType, int] = {animal: 0 for animal in AnimalType}

    for answer_id in answer_ids:
        option = find_answer(answer_id)
        if option is None:
            continue
        for animal, points in option.animal_scores.items():
            totals[animal] = totals.get(animal, 0) + points

    return totals
