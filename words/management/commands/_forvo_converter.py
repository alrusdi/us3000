from django.conf import settings
from words.models import Word, Pronunciation
import os
import json


def _concat_path(*args):
    return os.path.join(*args)


def _get_files_and_dirs_list(dir_path):
    return os.listdir(dir_path)


def _get_data_from_file(path_to_file):
    with open(path_to_file) as f:
        return f.read()


def _convert_str_to_dict(json_str, word):
    try:
        return json.loads(json_str)
    except json.decoder.JSONDecodeError:
        # logger_general_fails.error('Unexpected JSON format')
        # logger_od_convert_fails.error(word)
        print('Unexpected JSON format')
        # TODO replacing of print with logging is required


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
        # logger_general_fails.error('Unexpected JSON format')
        print('Unexpected JSON format')
    except TypeError:
        # logger_general_fails.error('Unexpected JSON format')
        print('Unexpected JSON format')
    # logger_od_convert_fails.error(word)
    # TODO replacing of print with logging is required


def _get_word_id(word):
    return Word.objects.filter(value=word).first()


def _save_data_to_db(word, word_mp3_path, pronunciation):
    new_word = Pronunciation(word=word)
    new_word.audio = word_mp3_path
    new_word.raw_od_data = pronunciation
    new_word.save()
    print(word)


def create_model_instance():
    sounds_dir_path = _concat_path(settings.BASE_DIR, 'media', 'sounds')
    words_sound_dirs_list = _get_files_and_dirs_list(sounds_dir_path)
    i = 0
    for word_sound_dir in words_sound_dirs_list:
        abs_word_sound_dir_path = _concat_path(sounds_dir_path, word_sound_dir)
        abs_word_od_path = _concat_path(settings.BASE_DIR, 'media', 'od',
                                        word_sound_dir + '.json')  # TODO replace with normal function
        word_id = _get_word_id(word_sound_dir)
        i += 1
        if word_id is None:
            continue
        od_json_str = _get_data_from_file(abs_word_od_path)
        od_json_dict = _convert_str_to_dict(od_json_str, word_sound_dir)
        word_pronunciation = _get_pronunc_from_json(od_json_dict, word_sound_dir)
        word_mp3_list = _get_files_and_dirs_list(abs_word_sound_dir_path)
        if i == 2:
            break
        for word_mp3 in word_mp3_list:
            word_mp3_path = _concat_path('sounds', word_sound_dir, word_mp3)
            _save_data_to_db(word_id, word_mp3_path, word_pronunciation)


# получить список директорий внутри папки sounds
# для каждой из этих директорий получить список файлов
# построить относительный путь к каждому файлу
# идти в БД и искать необходимое слово по value: word = Word.objects.filter(value='abandon')
# создаем и сохраняем экземпляры модели произношений: word2 = Word(pronunciation='some pronunciation') word2.save()
# первый вариант:
# pron = Prononciation()
# pron.word = Words.objects.get(value="someth")
# если есть только id: pron.word_id = 12
