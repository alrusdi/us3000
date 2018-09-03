from django.conf import settings
from django.core.management.base import BaseCommand
from words.models import Word, Pronunciation
import os
import json


class Command(BaseCommand):
    help = 'Import pronunciation from Forvo'

    def handle(self, *args, **options):
        create_model_instance()
        self.stdout.write(self.style.SUCCESS('Task completed'))


def concat_path(*args):
    return os.path.join(*args)


def get_files_and_dirs_list(dir_path):
    return os.listdir(dir_path)


def get_data_from_file(path_to_file):
    with open(path_to_file) as f:
        return f.read()


def convert_str_to_dict(json_str, word):
    try:
        return json.loads(json_str)
    except json.decoder.JSONDecodeError:
        # logger_general_fails.error('Unexpected JSON format')
        # logger_od_convert_fails.error(word)
        print('Unexpected JSON format')
        # TODO replacing of print with logging is required


def get_pronunc_from_json(json_word, word):
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


def get_word_id(word):
    return Word.objects.get(value=word)#.id


def save_data_to_db(word, word_dir_path):
    new_word = Pronunciation(word=word)
    new_word.audio = word_dir_path
    new_word.raw_od_data = {'some': 'json'}
    new_word.save()
    print(word)



def create_model_instance():
    word_dirs_path_list = []
    sounds_dir_path = concat_path(settings.BASE_DIR,
                                  'media',
                                  'sounds')
    words_sound_dirs_list = get_files_and_dirs_list(sounds_dir_path)
    for word_sound_dir in words_sound_dirs_list:
        abs_word_sound_dir_path = concat_path(sounds_dir_path, word_sound_dir)
        abs_word_od_path = concat_path(settings.BASE_DIR,
                                       'media', 'od',
                                       word_sound_dir + '.json')
        # word_dirs_path_list.append(abs_word_sound_dir_path)
        word_id = get_word_id(word_sound_dir)
        json_str = get_data_from_file(abs_word_od_path)
        json_dict = convert_str_to_dict(json_str, abs_word_od_path)
        word_pronunciation = get_pronunc_from_json(json_dict, word_sound_dir)
        word_mp3_list = get_files_and_dirs_list(word_sound_dir)
        # for word_mp3 in word_mp3_list:
        #     word_mp3_path = concat_path('sounds', word_dir, word_mp3)
        #     save_data_to_db(word_id, word_mp3_path)


# получить список директорий внутри папки sounds
# для каждой из этих директорий получить список файлов
# построить относительный путь к каждому файлу
# идти в БД и искать необходимое слово по value: word = Word.objects.filter(value='abandon')
# создаем и сохраняем экземпляры модели произношений: word2 = Word(pronunciation='some pronunciation') word2.save()
# первый вариант:
# pron = Prononciation()
# pron.word = Words.objects.get(value="someth")
# если есть только id: pron.word_id = 12
