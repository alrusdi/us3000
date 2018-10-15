import requests
import json
import queue
import threading
from ._words import words
import time
import os
from django.conf import settings
import logging


logger_forvo_fails = logging.getLogger("forvo_fails")
logger_general_fails = logging.getLogger("general")


class ForvoImporter(object):
    def __init__(self, word):
        self.word = word

    @staticmethod
    def _get_files_list_in_dir(dir_path):
        return os.listdir(dir_path)

    def _check_if_sounds_exist(self, dir_path):
        sound_dirs_list = self._get_files_list_in_dir(dir_path)
        return self.word in sound_dirs_list

    def get_html_from_forvo(self):
        url = 'https://api.forvo.com/demo'
        data = {
            "action": "word-pronunciations",
            "format": "json",
            "id_lang_speak": "39",
            "id_order": "",
            "limit": "",
            "rate": "",
            "send": "",
            "username": "",
            "word": self.word
        }
        try:
            result = requests.post(url, data=data)
            result.raise_for_status()
            if result.status_code == 200:
                return str(result.text)
        except requests.exceptions.ConnectionError:
            logger_general_fails.error('Connection error')
        except requests.exceptions.HTTPError as err:
            logger_general_fails.error('Following http error occurred: {}'.format(err))
        logger_forvo_fails.error(self.word)

    def get_raw_json_from_html(self, html):
        div_pos = html.find('class="intro"')
        pre_open_pos = html.find('<pre>', div_pos)
        pre_close_pos = html.find('</pre>', pre_open_pos + 1)
        if 0 < div_pos < pre_open_pos < pre_close_pos:
            return html[pre_open_pos + 6:pre_close_pos - 1]
        else:
            logger_general_fails.error('Unexpected HTML Response from Forvo')
            logger_forvo_fails.error(self.word)

    def normalize_raw_json(self, raw_json):
        json_str = raw_json.replace('&quot;', '"')
        try:
            return json.loads(json_str)
        except ValueError:
            logger_general_fails.error('Response from Forvo has'
                                       ' unexpected JSON format')
            logger_forvo_fails.error(self.word)

    def get_items_from_forvo_json(self, forvo_json):
        items = forvo_json.get('items', [])
        if len(items) > 0:
            return items
        else:
            logger_general_fails.error('JSON response from Forvo'
                                       ' has unexpected structure')
            logger_forvo_fails.error(self.word)

    def get_mp3_url_from_json(self, item):
        mp3_url_key = 'pathmp3'
        mp3_url = item.get(mp3_url_key, [])
        if len(mp3_url) > 0:
            return mp3_url.replace('\/', '/')
        else:
            logger_general_fails.error('JSON response from Forvo does not'
                                       ' have required keys')
            logger_forvo_fails.error(self.word)

    def get_mp3_from_forvo(self, mp3_url):
        try:
            mp3 = requests.get(mp3_url, stream=True)
            if mp3.status_code == 200:
                return mp3.content
        except requests.exceptions.ConnectionError:
            logger_general_fails.error('Connection error')
        except requests.exceptions.HTTPError as err:
            logger_general_fails.error('Following http error occurred: {}'.format(err))
        logger_forvo_fails.error(self.word)

    @classmethod
    def make_abs_sounds_dir_path(cls):
        return os.path.join(settings.BASE_DIR, 'media', 'sounds')

    @classmethod
    def is_path_exist(cls, dir_path):
        return os.path.exists(dir_path)

    @classmethod
    def is_there_dir_write_permissions(cls, dir_path):
        return os.access(dir_path, os.W_OK)

    def make_word_dir_path(self, sounds_dir_path):
        return os.path.join(sounds_dir_path, self.word)

    @classmethod
    def create_word_dir(cls, dir_path):
        return os.mkdir(dir_path)

    def make_mp3_abs_path(self, dir_path, item_number):
        mp3_file_name = '{}_{}.mp3'.format(self.word, item_number + 1)
        return os.path.join(dir_path, mp3_file_name)

    def save_mp3(self, mp3_full_path, mp3):
        try:
            with open(mp3_full_path, 'wb') as f:
                f.write(mp3)
        except AssertionError:
            raise  # for testing
        except Exception as err:
            self.write_to_log('Something went wrong: {}'.format(err))

    def write_to_log(self, log_message):
        logger_general_fails.error(log_message)
        logger_forvo_fails.error(self.word)

    def save_result(self, item, item_number):
        mp3_url = self.get_mp3_url_from_json(item)
        if mp3_url is None:
            return
        mp3 = self.get_mp3_from_forvo(mp3_url)
        if mp3 is None:
            return
        abs_sounds_dir_path = self.make_abs_sounds_dir_path()
        if not self.is_path_exist(abs_sounds_dir_path):
            self.write_to_log("Path does not exist: '{}'".format(
                abs_sounds_dir_path))
            return
        if not self.is_there_dir_write_permissions(abs_sounds_dir_path):
            self.write_to_log("Permission denied: '{}'".format(
                abs_sounds_dir_path))
            return
        word_dir_path = self.make_word_dir_path(abs_sounds_dir_path)
        if not self.is_path_exist(word_dir_path):
            self.create_word_dir(word_dir_path)
        mp3_abs_path = self.make_mp3_abs_path(word_dir_path, item_number)
        self.save_mp3(mp3_abs_path, mp3)

    def import_sound(self):
        sounds_dir = self.make_abs_sounds_dir_path()
        if self._check_if_sounds_exist(sounds_dir):
            return
        html = self.get_html_from_forvo()
        if html is None:
            return
        raw_json = self.get_raw_json_from_html(html)
        if raw_json is None:
            return
        forvo_json = self.normalize_raw_json(raw_json)
        if forvo_json is None:
            return
        items = self.get_items_from_forvo_json(forvo_json)
        if items is None:
            return
        item_number = 0
        for item in items:
            if item.get('code', '') != 'en' or item.get(
                    'country', '') != 'United States':
                continue
            self.save_result(item, item_number)
            item_number += 1
            if item_number > 4:
                break


class MultithreadingParser:
    def __init__(self, threads_count=50):
        self.queue = self._make_queue()
        if self.queue.qsize() < threads_count:
            self.threads_count = self.queue.qsize()
        else:
            self.threads_count = threads_count

    @staticmethod
    def _make_queue():
        q = queue.Queue()
        for word in words:
            if ' ' in word:
                continue
            q.put_nowait(word)
        return q

    def run(self):
        threads = []
        for i in range(self.threads_count):
            thread_name = 'thread_{}'.format(i - 1)
            thread = threading.Thread(
                target=self.worker, args=(thread_name, ), daemon=True)
            thread.start()
            threads.append(thread)
        while True:
            if self.queue.qsize() < 1:
                for _ in range(self.threads_count):
                    self.queue.put(None)
                for thread in threads:
                    thread.join()
                return

    def worker(self, thread_name):
        while True:
            task = self.queue.get(block=True)
            if task is None:
                break
            fi = ForvoImporter(task)
            try:
                fi.import_sound()
                time.sleep(1)
            except Exception as err:
                logger_general_fails.error('Following error occurred: {}'.format(err))
            self.queue.task_done()
