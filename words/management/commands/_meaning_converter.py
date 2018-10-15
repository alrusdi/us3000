import os
import json
import logging
from django.conf import settings
from words.models import Meaning, Word


logger_meaning_convert_fails = logging.getLogger("meaning_convert_fails")
logger_general_fails = logging.getLogger("general")


def _concat_path(*args):
    return os.path.join(*args)


def _get_files_list_in_dir(dir_path):
    return os.listdir(dir_path)


def check_if_meanings_exist_in_db(word):
    return Meaning.objects.filter(word__value=word).exists()


def _get_data_from_file(path_to_file):
    with open(path_to_file) as f:
        return f.read()


def _convert_str_to_dict(json_str, word):
    try:
        return json.loads(json_str)
    except json.decoder.JSONDecodeError:
        logger_general_fails.error('Unexpected JSON format')
        logger_meaning_convert_fails.error(word)


def _get_meaning_from_json(json_word, word):
    meanings_list = []
    try:
        lexical_entries = json_word.get('results')[0].get('lexicalEntries')
        for lexical_entry in lexical_entries:
            entries = lexical_entry.get('entries')
            for entry in entries:
                senses = entry.get('senses')
                for sense in senses:
                    meaning = sense.get('definitions')
                    examples = sense.get('examples')
                    if meaning is None:
                        meaning = sense.get('short_definitions')
                    if meaning is None:
                        meaning = sense.get('crossReferenceMarkers')
                    if meaning is not None:
                        meanings_list.append(
                            dict(meaning=meaning[0],
                                 example=examples)
                        )
                    subsenses = sense.get('subsenses')
                    if subsenses is None:
                        continue
                    for subsense in subsenses:
                        meaning = subsense.get('definitions')
                        examples = subsense.get('examples')
                        if meaning is None:
                            continue
                        meanings_list.append(
                            dict(meaning=meaning[0],
                                 example=examples)
                        )
        if len(meanings_list) == 0:
            logger_general_fails.error('There is no meaning for "{}" word'
                                       .format(word.capitalize()))
            logger_meaning_convert_fails.error(word)
        return meanings_list
    except AttributeError:
        logger_general_fails.error('Unexpected JSON format')
    except TypeError:
        logger_general_fails.error('Unexpected JSON format')
    logger_meaning_convert_fails.error(word)


def _save_data_to_db(word, meanings_list):
    for i, meaning in enumerate(meanings_list):
        new_meaning = Meaning(word=word)
        new_meaning.value = meaning['meaning']
        new_meaning.order = i
        new_meaning.examples = meaning['example']
        new_meaning.save()


def _get_word_model_value(word):
    return Word.objects.filter(value=word).first()


def add_data_to_meaning_model():
    work_dir_path = _concat_path(settings.BASE_DIR,
                                 'media', 'od')
    files_list = _get_files_list_in_dir(work_dir_path)
    for i, file in enumerate(files_list):
        word = file[:-5]
        if check_if_meanings_exist_in_db(word):
            continue
        word_model_value = _get_word_model_value(word)
        if not word_model_value:
            continue
        abs_file_path = _concat_path(work_dir_path, file)
        json_str = _get_data_from_file(abs_file_path)
        json_dict = _convert_str_to_dict(json_str, word)
        meanings = _get_meaning_from_json(json_dict, word)
        _save_data_to_db(word_model_value, meanings)
