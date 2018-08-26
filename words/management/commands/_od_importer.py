import requests
import os


class ODImporter:
    def __init__(self, word):
        self.word = word

    def get_article(self, app_id, app_key):
        language = 'en'
        url = '/'.join(('https://od-api.oxforddictionaries.com:443/api/v1/entries',
                        language, self.word.lower()))
        response_text = ''

        if ' ' in self.word:
            return "Word contains space", response_text

        try:
            r = requests.get(url, headers={'app_id': app_id,
                                           'app_key': app_key})
            r.raise_for_status()
            status_message = 'Data successfully saved'
            response_text = r.text
        except requests.exceptions.ConnectionError:
            status_message = 'Connection error'
        except requests.exceptions.HTTPError as err:
            if str(err) == '404':
                status_message = 'Specified word does not exist in Oxford Dictionary'
            else:
                status_message = 'HTTP error {} occurred'.format(err)
        return status_message, response_text

    def make_abs_path(self, abs_dir_path):
        return '{}/{}.json'.format(abs_dir_path, self.word)

    def save_article(self, file_path, word_dict):
        with open(file_path, 'w') as f:
            f.write(word_dict)

    def create_word_article(self, abs_dir_path, app_id, app_key):
        if not os.path.exists(abs_dir_path):
            return "Path does not exist: '{}'".format(abs_dir_path)
        if not os.access(abs_dir_path, os.W_OK):
            return "Permission denied: '{}'".format(abs_dir_path)
        status_message, word_article = self.get_article(app_id, app_key)
        if word_article != '':
            abs_file_path = self.make_abs_path(abs_dir_path)
            self.save_article(abs_file_path, word_article)
        return status_message
