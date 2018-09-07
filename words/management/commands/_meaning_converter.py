import os
import json
import logging
from django.conf import settings
from words.models import Meaning, Word


# TODO correct configuring logging required
# logger_od_convert_fails = logging.getLogger("od_convert_fails")
# logger_general_fails = logging.getLogger("general")


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
        print('Unexpected JSON format')
        # TODO correct configuring logging required
        # logger_general_fails.error('Unexpected JSON format')
        # logger_od_convert_fails.error(word)


def _get_meaning_from_json(json_word, word):
    meanings_list = []
    try:
        senses = json_word.get('results')[0].get('lexicalEntries')[0].get(
            'entries')[0].get('senses')#[0]
        for sense in senses:
            meaning = sense.get('definitions')[0]
            if meaning is None:
                continue
            meanings_list.append(meaning)
            subsenses = sense.get('subsenses')
            if subsenses is None:
                continue
            for subsense in subsenses:
                meaning = subsense.get('definitions')[0]
                if meaning is None:
                    continue
                meanings_list.append(meaning)
        return meanings_list
        # meanings = sense.get('definitions')
        # if meanings is not None:
        #     return meanings[0]
        # meanings = sense.get('short_definitions')
        # if meanings is not None:
        #     return meanings[0]
        # meanings = sense.get('crossReferenceMarkers')
        # if meanings is not None:
        #     return meanings[0]
    except AttributeError:
        print('Unexpected JSON format')
        # logger_general_fails.error('Unexpected JSON format')
    except TypeError:
        print('Unexpected JSON format')
    #     logger_general_fails.error('Unexpected JSON format')
    # logger_od_convert_fails.error(word)


def _save_data_to_db(word, meanings_list):
    print(word)
    for i, meaning in enumerate(meanings_list):
        new_meaning = Meaning(word=word)
        new_meaning.value = meaning
        new_meaning.order = i
        new_meaning.save()


def _get_word_model_value(word):
    return Word.objects.filter(value=word).first()


def add_data_to_meaning_model():
    work_dir_path = _concat_path(settings.BASE_DIR,
                                 'media', 'od')
    files_list = _get_files_list_in_dir(work_dir_path)
    for i, file in enumerate(files_list):
        word = file[:-5]
        word_model_value = _get_word_model_value(word)
        abs_file_path = _concat_path(work_dir_path, file)
        json_str = _get_data_from_file(abs_file_path)
        json_dict = _convert_str_to_dict(json_str, word)
        meanings = _get_meaning_from_json(json_dict, word)
        # print(meanings)
        if i == 20:
            break
        _save_data_to_db(word_model_value, meanings)
