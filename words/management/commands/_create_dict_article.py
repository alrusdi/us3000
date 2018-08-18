import requests
from main import settings_local as settings
import os


class Word:
    def __init__(self, word):
        self.word = word

    def get_dict(self):
        app_id = settings.OXFORD_DICTIONARY_APP_ID
        app_key = settings.OXFORD_DICTIONARY_APP_KEY
        language = 'en'
        url = '/'.join(('https://od-api.oxforddictionaries.com:443/api/v1/entries',
                        language, self.word.lower()))
        response_text = ''

        try:
            r = requests.get(url, headers={'app_id': app_id, 'app_key': app_key})
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

    def get_abs_file_path(self):
        full_filename = '.'.join((self.word, 'json'))
        return os.path.join(settings.BASE_DIR, 'media', 'od', full_filename)

    def save_dict(self, file_path, word_dict):
        with open(file_path, 'w') as f:
            f.write(word_dict)

    def create_word_article(self):
        status_message, word_dict = self.get_dict()
        if word_dict != '':
            abs_file_path = self.get_abs_file_path()
            self.save_dict(abs_file_path, word_dict)
        return status_message
