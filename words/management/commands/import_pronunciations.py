from django.core.management.base import BaseCommand
from ._forvo_importer import MultithreadingParser


class Command(BaseCommand):
    help = 'Import pronunciation from Forvo'

    def handle(self, *args, **options):
        MultithreadingParser().run()
        self.stdout.write(self.style.SUCCESS('Task completed'))
