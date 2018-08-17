from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Import dictionaries articles from Oxford Dictionary'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('{}'.format(settings.OXFORD_DICTIONARY_APP_ID)))
        self.stdout.write(self.style.SUCCESS('{}'.format(settings.BASE_DIR)))

        output_dir = os.path.join(settings.BASE_DIR, 'media', 'od')
