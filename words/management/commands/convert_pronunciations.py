from django.core.management.base import BaseCommand
from words.management.commands._forvo_converter import create_model_instance


class Command(BaseCommand):
    help = 'Import pronunciation from Forvo'

    def handle(self, *args, **options):
        create_model_instance()
        self.stdout.write(self.style.SUCCESS('Task completed'))
