from django.core.management.base import BaseCommand
from django.conf import settings
import os
from ._od_importer import ODImporter, check_if_od_article_exist
from ._words import words
import time
import logging


logger_od_fails = logging.getLogger("od_fails")
logger_general_fails = logging.getLogger("general")


class Command(BaseCommand):
    help = 'Import dictionary articles from Oxford Dictionary'

    def handle(self, *args, **options):
        dir_path = os.path.join(settings.BASE_DIR, 'media', 'od')
        od_conf = settings.OXFORD_DICTIONARY_CONFIG
        next_od_account_idx = 0
        number_of_consecutive_errors = 0
        for i, word in enumerate(words):
            if check_if_od_article_exist(word, dir_path):
                continue
            if ' ' in word:
                continue
            word_obj = ODImporter(word)

            conf = od_conf[next_od_account_idx]
            next_od_account_idx += 1
            if next_od_account_idx == len(od_conf):
                next_od_account_idx = 0

            response_message = word_obj.create_word_article(
                dir_path,
                conf['app_id'],
                conf['app_key']
            )
            if response_message == 'Data successfully saved':
                number_of_consecutive_errors = 0
            else:
                logger_general_fails.error(response_message)
                logger_od_fails.info(word)
                number_of_consecutive_errors += 1
                if number_of_consecutive_errors > 5:
                    logger_general_fails.error(
                        '5 consecutive errors got. Script execution stopped.')
                    break
            time.sleep(1)
