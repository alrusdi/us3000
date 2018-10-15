from django.core.management.base import BaseCommand
from ._od_converter import convert_and_save_od_article


class Command(BaseCommand):
    help = 'Convert and save OD article'

    def handle(self, *args, **options):
        convert_and_save_od_article()
        self.stdout.write(self.style.SUCCESS('Task completed'))
