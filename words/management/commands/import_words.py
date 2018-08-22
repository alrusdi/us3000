from django.core.management.base import BaseCommand
from django.conf import settings
import os
from ._od_importer import Word
from ._words import words
import time


class Command(BaseCommand):
    help = 'Import dictionary articles from Oxford Dictionary'

    def handle(self, *args, **options):
        dir_path = os.path.join(settings.BASE_DIR, 'media', 'od')
        app_id = (settings.OXFORD_DICTIONARY_APP_ID_1,
                  settings.OXFORD_DICTIONARY_APP_ID_2)
        app_key = (settings.OXFORD_DICTIONARY_APP_KEY_1,
                   settings.OXFORD_DICTIONARY_APP_KEY_2)
        number_of_requested_articles = 5
        for i in range(number_of_requested_articles):
            iteration_id = i % 2
            word = Word(words[i])
            response_status = word.create_word_article(dir_path,
                                                       app_id[iteration_id],
                                                       app_key[iteration_id])
            self.stdout.write(self.style.SUCCESS('{}. {}: {}'.format(
                i, word.word, response_status)))
            time.sleep(1)
