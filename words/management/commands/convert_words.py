from django.core.management.base import BaseCommand
from ._od_converter import create_fixture


class Command(BaseCommand):
    help = 'Convert JSON from OD to fixture'

    def handle(self, *args, **options):
        create_fixture()
        self.stdout.write(self.style.SUCCESS('Task completed'))
