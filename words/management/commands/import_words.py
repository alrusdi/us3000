from django.core.management.base import BaseCommand
from django.conf import settings
import os
from ._od_importer import Word
from ._words import words


class Command(BaseCommand):
    help = 'Import dictionary articles from Oxford Dictionary'

    def handle(self, *args, **options):
        dir_path = os.path.join(settings.BASE_DIR, 'media', 'od')
        app_id = settings.OXFORD_DICTIONARY_APP_ID
        app_key = settings.OXFORD_DICTIONARY_APP_KEY
        number_of_requested_articles = 60
        for i in range(number_of_requested_articles):
            word = Word(words[i])
            response_status = word.create_word_article(dir_path,
                                                       app_id,
                                                       app_key)
            self.stdout.write(self.style.SUCCESS('{}: {}'.format(
                word.word, response_status)))
