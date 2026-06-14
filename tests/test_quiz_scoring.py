from bot.models import AnimalType, UserSession
from bot.quiz_data import find_answer, get_question_count
from bot.quiz_scoring import calculate_result, preview_scores


def test_calculate_result_elephant():
    session = UserSession()
    answers = [
        "weekend_team",
        "friends_leader",
        "food_varied",
        "surprise_calm",
        "habitat_savanna",
        "morning_social",
    ]
    session.selected_answer_ids.extend(answers)
    assert calculate_result(session) == AnimalType.ELEPHANT


def test_calculate_result_porcupine():
    from bot.models import UserSession

    session = UserSession()
    answers = [
        "weekend_solo",
        "friends_unique",
        "food_sweet",
        "surprise_retreat",
        "habitat_burrow",
        "morning_quiet",
    ]
    session.selected_answer_ids.extend(answers)
    assert calculate_result(session) == AnimalType.PORCUPINE


def test_preview_scores():
    scores = preview_scores(["weekend_team", "morning_social"])
    assert scores[AnimalType.ELEPHANT] == 5
    assert scores[AnimalType.FLAMINGO] == 5


def test_quiz_has_six_questions():
    assert get_question_count() == 6


def test_find_answer():
    option = find_answer("weekend_team")
    assert option is not None
    assert option.option_id == "weekend_team"
    assert AnimalType.ELEPHANT in option.animal_scores
