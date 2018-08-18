import requests
from main import settings_local as settings
import os
from ._words import words


def get_dict(word_id):
    app_id = settings.OXFORD_DICTIONARY_APP_ID
    app_key = settings.OXFORD_DICTIONARY_APP_KEY
    language = 'en'
    url = '/'.join(('https://od-api.oxforddictionaries.com:443/api/v1/entries',
                    language, word_id.lower()))
    response_text = ''

    try:
        r = requests.get(url, headers = {'app_id': app_id, 'app_key': app_key})
        r.raise_for_status()
        status_message = 'Data successfully saved'
        response_text = r.text
    except requests.exceptions.ConnectionError:
        status_message = 'Connection error'
    except requests.exceptions.HTTPError as err:
        if r.status_code == 404:
            status_message = 'Specified word does not exist in Oxford Dictionary'
        else:
            status_message = 'HTTP error occurred. Response is: {}'.format(
                err.response.content.decode())
    return status_message, response_text


def get_abs_file_path(filename):
    full_filename = '.'.join((filename, 'json'))
    return os.path.join(settings.BASE_DIR, 'media', 'od', full_filename)


def save_dict(file_path, word_dict):
    with open(file_path, 'w') as f:
        f.write(word_dict)


def save_article():
    word = words[0]
    status_message, word_dict = get_dict(word)
    if word_dict != '':
        abs_file_path = get_abs_file_path(word)
        save_dict(abs_file_path, word_dict)
    return status_message


if __name__ == '__main__':
    save_article()
