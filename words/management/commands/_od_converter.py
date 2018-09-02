import os
import json
import logging
from django.conf import settings


logger_od_convert_fails = logging.getLogger("od_convert_fails")
logger_general_fails = logging.getLogger("general")


def concat_path(*args):
    return os.path.join(*args)


def get_files_list_in_dir(dir_path):
    return os.listdir(dir_path)


def get_data_from_file(path_to_file):
    with open(path_to_file) as f:
        return f.read()


def convert_str_to_dict(json_str, word):
    try:
        a = json.loads(json_str)
        return a
    except json.decoder.JSONDecodeError:
        logger_general_fails.error('Unexpected JSON format')
        logger_od_convert_fails.error(word)


def get_meaning_from_json(json_word, word):
    try:
        meanings = json_word.get('results')[0].get('lexicalEntries')[0].get(
            'entries')[0].get('senses')[0].get('definitions')
        if meanings is not None:
            return meanings[0]
        return json_word.get('results')[0].get('lexicalEntries')[0].get(
            'entries')[0].get('senses')[0].get('short_definitions')[0]
    except AttributeError:
        logger_general_fails.error('Unexpected JSON format')
    except TypeError:
        logger_general_fails.error('Unexpected JSON format')
    logger_od_convert_fails.error(word)


def get_spelling_from_json(json_word, word):
    try:
        return json_word.get('results')[0].get('lexicalEntries')[0].get(
            'pronunciations')[0].get('phoneticSpelling')
    except AttributeError:
        logger_general_fails.error('Unexpected JSON format')
    except TypeError:
        logger_general_fails.error('Unexpected JSON format')
    logger_od_convert_fails.error(word)


def make_word_dict(word_number, word, meaning, spelling, raw_json):
    return {
        "model": "words.word",
        "pk": word_number,
        "fields": {
            "value": "{}".format(word),
            "general_meaning": "{}".format(meaning),
            "spelling": "{}".format(spelling),
            "raw_od_article": "{}".format(raw_json)
        }
    }


def add_word_to_fixture(output_list, word_dict):
    return output_list.append(word_dict)


def save_fixture(file_path, data):
    with open(file_path, 'w') as f:
        f.write(data)


def create_fixture():
    words_fixture = []
    work_dir_path = concat_path(settings.BASE_DIR,  # replace '/home/t0lik/us3000/us3000_project'
                                'media', 'od')                        # with settings.BASE_DIR,
    files_list = get_files_list_in_dir(work_dir_path)
    for i, file in enumerate(files_list):
        word = file[:-5]
        abs_file_path = concat_path(work_dir_path, file)
        json_str = get_data_from_file(abs_file_path)
        json_dict = convert_str_to_dict(json_str, word)
        meaning = get_meaning_from_json(json_dict, word)
        spelling = get_spelling_from_json(json_dict, word)
        word_dict = make_word_dict(i, word, meaning, spelling, json_dict)
        add_word_to_fixture(words_fixture, word_dict)
        abs_fixture_path = concat_path(settings.BASE_DIR,
                                       'words', 'fixtures', 'words.json')
        formatted_fixture = json.dumps(words_fixture, sort_keys=True,
                                       indent=4, ensure_ascii=False)
        save_fixture(abs_fixture_path, formatted_fixture)
