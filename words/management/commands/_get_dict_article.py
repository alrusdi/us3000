import requests
from main import settings_local as settings
import os
from ._words import words


def get_dict(word):
    app_id = settings.OXFORD_DICTIONARY_APP_ID
    app_key = settings.OXFORD_DICTIONARY_APP_KEY
    language = 'en'
    word_id = word

    url = '/'.join(('https://od-api.oxforddictionaries.com:443/api/v1/entries',
                    language, word_id.lower()))
    try:
        r = requests.get(url, headers = {'app_id': app_id, 'app_key': app_key})
        status_code, text = r.status_code, r.text
    except requests.exceptions.ConnectionError:
        status_code, text = 434, ''
    return status_code, text


def get_abs_file_path(filename):
    full_filename = '.'.join((filename, 'json'))
    return os.path.join(settings.BASE_DIR, 'media', 'od', full_filename)


def save_dict(file_path, word_dict):
    with open(file_path, 'w') as f:
        f.write(word_dict)


def save_article():
    word = words[0]
    status_code, word_dict = get_dict(word)
    if status_code == 200:
        abs_file_path = get_abs_file_path(word)
        save_dict(abs_file_path, word_dict)
        status_message = 'Data successfully saved'
    elif status_code == 404:
        status_message = 'Word is not exist in Oxford Dictionary'
    elif status_code == 434:
        status_message = 'Oxford Dictionary is not available'
    else:
        status_message = 'Unknown error occurred'
    return status_message


if __name__ == '__main__':
    save_article()
