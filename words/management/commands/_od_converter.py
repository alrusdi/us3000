import os
import json
import logging
from django.conf import settings

from words.models import Word

logger_od_convert_fails = logging.getLogger("od_convert_fails")
logger_general_fails = logging.getLogger("general")


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
    print(word)
    spelling = ""
    try:
        lexical_entries = json_word.get('results')[0].get('lexicalEntries')
        for lexical_entry in lexical_entries:
            # entries = lexical_entry.get('entries')
            pronunciations = lexical_entry.get('pronunciations')
            if pronunciations is None:
                continue
            for pronunciation in pronunciations:
                spelling = pronunciation.get('phoneticSpelling')
                if spelling is None:
                    continue
                else:
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


def make_word_dict(word_number, word, spelling, raw_json): # TODO remove
    return {
        "model": "words.word",
        # "pk": word_number,
        "fields": {
            "value": "{}".format(word),
            "spelling": "{}".format(spelling),
            "raw_od_article": "{}".format(raw_json)
        }
    }


def _save_data_to_db(word, spelling, raw_json):
    new_word = Word()
    new_word.value = word
    new_word.spelling = spelling
    new_word.raw_od_article = raw_json
    new_word.save()


def add_word_to_fixture(output_list, word_dict): # TODO remove
    return output_list.append(word_dict)


def save_fixture(file_path, data): # TODO remove
    with open(file_path, 'w') as f:
        f.write(data)


def create_fixture(): # TODO change function name
    words_fixture = [] # TODO remove
    work_dir_path = _concat_path(settings.BASE_DIR,
                                 'media', 'od')
    files_list = _get_files_list_in_dir(work_dir_path)
    for i, file in enumerate(files_list):  # TODO remove i and enumerate
        word = file[:-5]
        abs_file_path = _concat_path(work_dir_path, file)
        json_str = _get_data_from_file(abs_file_path)
        json_dict = _convert_str_to_dict(json_str, word)
        spelling = _get_spelling_from_json(json_dict, word)
        # word_dict = make_word_dict(i + 1, word, spelling, json_dict)
        # add_word_to_fixture(words_fixture, word_dict)
        # normalized_json = json.dumps(json_dict)
        _save_data_to_db(word, spelling, json.dumps(json_dict))
        if i == 10:
            break
        # if len(words_fixture) == 1:
        #     break
        # abs_fixture_path = concat_path(settings.BASE_DIR,
        #                                'words', 'fixtures', 'words.json')
        # formatted_fixture = json.dumps(words_fixture, sort_keys=True,
        #                                indent=4, ensure_ascii=False)
        # save_fixture(abs_fixture_path, formatted_fixture)
