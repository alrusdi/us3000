import os
import json
import logging
from django.conf import settings
from words.models import Word

logger_od_convert_fails = logging.getLogger("od_convert_fails")
logger_general_fails = logging.getLogger("general")


def _check_if_word_exist_in_db(word):
    return Word.objects.filter(value=word).exists()


def _concat_path(*args):
    return os.path.join(*args)


def _get_files_list_in_dir(dir_path):
    return os.listdir(dir_path)


def _get_data_from_file(path_to_file):
    with open(path_to_file) as f:
        return f.read()


def _convert_str_to_dict(json_str, word):
    try:
        return json.loads(json_str)
    except json.decoder.JSONDecodeError:
        logger_general_fails.error('Unexpected JSON format')
        logger_od_convert_fails.error(word)


def _get_spelling_from_json(json_word, word):
    spelling = ""
    try:
        lexical_entries = json_word.get('results')[0].get('lexicalEntries')
        for lexical_entry in lexical_entries:
            pronunciations = lexical_entry.get('pronunciations')
            if pronunciations:
                for pronunciation in pronunciations:
                    if 'phoneticSpelling' not in pronunciation:
                        continue
                    spelling = pronunciation.get('phoneticSpelling')
                    break
            if spelling:
                break
            entries = lexical_entry.get('entries')
            if entries:
                for entry in entries:
                    pronunciations = entry.get('pronunciations')
                    if pronunciations:
                        for pronunciation in pronunciations:
                            if 'phoneticSpelling' not in pronunciation:
                                continue
                            spelling = pronunciation.get('phoneticSpelling')
                            break
                        if spelling:
                            break
                    senses = entry.get('senses')
                    if senses:
                        for sense in senses:
                            pronunciations = sense.get('pronunciations')
                            if pronunciations:
                                for pronunciation in pronunciations:
                                    if 'phoneticSpelling' not in pronunciation:
                                        continue
                                    spelling = pronunciation.get('phoneticSpelling')
                                    break
                                if spelling:
                                    break

        if not bool(spelling):
            logger_general_fails.error('There is no spelling for "{}" word'
                                       .format(word.capitalize()))
            logger_od_convert_fails.error(word)
        return spelling
    except AttributeError:
        logger_general_fails.error('Unexpected JSON format')
    except TypeError:
        logger_general_fails.error('Unexpected JSON format')
    logger_od_convert_fails.error(word)


def _save_data_to_db(word, spelling, raw_json):
    new_word = Word()
    new_word.value = word
    new_word.spelling = spelling
    new_word.raw_od_article = raw_json
    new_word.save()


def convert_and_save_od_article():
    work_dir_path = _concat_path(settings.BASE_DIR,
                                 'media', 'od')
    file_names_list = _get_files_list_in_dir(work_dir_path)
    for file_name in file_names_list:
        word = file_name[:-5]
        if _check_if_word_exist_in_db(word):
            continue
        abs_file_path = _concat_path(work_dir_path, file_name)
        json_str = _get_data_from_file(abs_file_path)
        json_dict = _convert_str_to_dict(json_str, word)
        spelling = _get_spelling_from_json(json_dict, word)
        _save_data_to_db(word, spelling, json_dict)
