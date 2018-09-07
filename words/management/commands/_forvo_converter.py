import logging
import os
import json
from django.conf import settings
from words.models import Word, Pronunciation


logger_pronunc_convert_fails = logging.getLogger("pronunc_convert_fails")
logger_general_fails = logging.getLogger("general")


def _concat_path(*args):
    return os.path.join(*args)


def _make_json_filename(word):
    return '{}.json'.format(word)


def _get_dir_items_list(dir_path):
    return os.listdir(dir_path)


def check_if_pronunc_exist_in_db(word):
    return Pronunciation.objects.filter(word__value=word).exists()


def _get_data_from_file(path_to_file):
    with open(path_to_file) as f:
        return f.read()


def _convert_str_to_dict(json_str, word):
    try:
        return json.loads(json_str)
    except json.decoder.JSONDecodeError:
        logger_general_fails.error('Unexpected JSON format')
        logger_pronunc_convert_fails.error(word)


def _get_pronunc_from_json(json_word, word):
    try:
        lexical_entry = json_word.get('results')[0].get('lexicalEntries')[0]
        pronunciations = lexical_entry.get('pronunciations')
        if pronunciations is not None:
            return pronunciations
        entries = lexical_entry.get('entries')
        if entries is not None:
            return entries[0].get('pronunciations')
    except AttributeError:
        logger_general_fails.error('Unexpected JSON format')
    except TypeError:
        logger_general_fails.error('Unexpected JSON format')
    logger_pronunc_convert_fails.error(word)


def _get_word_model_value(word):
    return Word.objects.filter(value=word).first()


def _save_data_to_db(word, word_mp3_path, pronunciation_dict):
    new_word = Pronunciation(word=word)
    new_word.audio = word_mp3_path
    new_word.raw_od_data = pronunciation_dict
    new_word.save()


def add_data_to_pronunciation_model():
    sounds_dir_path = _concat_path(settings.BASE_DIR, 'media', 'sounds')
    words_list = _get_dir_items_list(sounds_dir_path)
    for word in words_list:
        if check_if_pronunc_exist_in_db(word):
            continue
        abs_word_sound_dir_path = _concat_path(sounds_dir_path, word)
        json_filename = _make_json_filename(word)
        abs_word_od_path = _concat_path(settings.BASE_DIR, 'media',
                                        'od', json_filename)
        word_model_value = _get_word_model_value(word)
        if word_model_value is None:
            continue
        od_json_str = _get_data_from_file(abs_word_od_path)
        od_json_dict = _convert_str_to_dict(od_json_str, word)
        word_pronunciation_dict = _get_pronunc_from_json(od_json_dict, word)
        word_mp3_list = _get_dir_items_list(abs_word_sound_dir_path)
        for word_mp3 in word_mp3_list:
            word_mp3_path = _concat_path('sounds', word, word_mp3)
            _save_data_to_db(word_model_value, word_mp3_path,
                             word_pronunciation_dict)
