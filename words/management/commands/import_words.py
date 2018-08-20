from django.core.management.base import BaseCommand
from ._create_dict_article import Word
from ._words import words


class Command(BaseCommand):
    help = 'Import dictionary articles from Oxford Dictionary'

    def handle(self, *args, **options):
        for i in range(3000):
            word = Word(words[i])
            response_status = word.create_word_article()
            self.stdout.write(self.style.SUCCESS('{}: {}'.format(
                word.word, response_status)))
