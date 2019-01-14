import random

from django.db.models import F

from words.models import WordLearningState, Word
from main.settings import WORDS_NUMBER, WORDS_TO_REPEAT_BOUND, WORDS_NUMBER_TO_REPEAT


def _get_known_words_ids(user):
    return WordLearningState.objects.filter(
        user=user,
        is_user_know_meaning=True,
        is_user_know_pronunciation=True
    ).values_list(
        'id', flat=True
    )


def _get_all_words_ids():
    return Word.objects.filter(
        is_active=True
    ).values_list(
        'id', flat=True
    )


def _calculate_new_known_words_ratio(known_words_number, all_words_number):
    if known_words_number < WORDS_TO_REPEAT_BOUND:
        known_words_needed = 0
        new_words_needed = WORDS_NUMBER
    elif all_words_number - known_words_number > WORDS_NUMBER - WORDS_NUMBER_TO_REPEAT:
        new_words_needed = WORDS_NUMBER - WORDS_NUMBER_TO_REPEAT
        known_words_needed = WORDS_NUMBER_TO_REPEAT
    elif all_words_number - known_words_number < WORDS_NUMBER - WORDS_NUMBER_TO_REPEAT:
        new_words_needed = all_words_number - known_words_number
        known_words_needed = WORDS_NUMBER - new_words_needed
    else:
        raise Exception('unexpected words ratio')
    return known_words_needed, new_words_needed


def _get_random_new_words(known_words_ids, all_words_ids, new_words_needed):
    new_ids = set(all_words_ids) - set(known_words_ids)
    needed_ids = random.sample(new_ids, new_words_needed)
    return list(needed_ids)


def _save_word_learning_state_to_db(needed_ids, user):
    new_states = []
    for word_id in needed_ids:
        if WordLearningState.objects.filter(word_id=word_id, user=user).update(usage_count=F('usage_count') + 1):
            continue
        new_states.append(WordLearningState(user=user, word_id=word_id, usage_count=1))
    WordLearningState.objects.bulk_create(new_states)


def _get_words_to_repeat(number_words_to_repeat, user):
    words = WordLearningState.objects.filter(
        user=user,
        is_user_know_meaning=True,
        is_user_know_pronunciation=True
    ).order_by(
        'usage_count'
    ).values_list(
        'id', flat=True
    )
    words = words[:number_words_to_repeat]
    return list(words)


def get_words_qs(user):
    training_session_words = WordLearningState.objects.filter(
        training_session=True)
    if training_session_words:
        return training_session_words
    known_words_ids = _get_known_words_ids(user)
    all_words_ids = _get_all_words_ids()
    known_words_needed, new_words_needed = _calculate_new_known_words_ratio(
        len(known_words_ids),
        len(all_words_ids)
    )
    random_new_words = _get_random_new_words(known_words_ids,
                                             all_words_ids,
                                             new_words_needed)
    _save_word_learning_state_to_db(random_new_words, user)
    words_to_repeat = _get_words_to_repeat(known_words_needed, user)
    words_for_learning = random_new_words + words_to_repeat
    random.shuffle(words_for_learning)
    pronc = WordLearningState.objects.filter(
        word_id__in=words_for_learning
    ).prefetch_related(
        'word',
        'word__pronunciation_set',
        'word__meaning_set'
    )
    pronc.update(training_session=True)
    return pronc
