from django.core.management.base import BaseCommand
from words.management.commands._forvo_converter import add_data_to_pronunciation_model


class Command(BaseCommand):
    help = 'Import pronunciation from Forvo'

    def handle(self, *args, **options):
        add_data_to_pronunciation_model()
        self.stdout.write(self.style.SUCCESS('Task completed'))
