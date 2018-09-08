from django.core.management.base import BaseCommand
from words.management.commands._meaning_converter import add_data_to_meaning_model


class Command(BaseCommand):
    help = 'Upload meanings from OD json to db'

    def handle(self, *args, **options):
        add_data_to_meaning_model()
        self.stdout.write(self.style.SUCCESS('Task completed'))
