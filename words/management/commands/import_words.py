from django.core.management.base import BaseCommand
from ._get_dict_article import save_article


class Command(BaseCommand):
    help = 'Import dictionary articles from Oxford Dictionary'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('{}'.format(save_article())))
