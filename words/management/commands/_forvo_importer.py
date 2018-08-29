import requests
import json
import queue
import threading
from ._words import words
import time
import os
from django.conf import settings


class ForvoImporter(object):
    def __init__(self, word):
        self.word = word

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
            print('Connection error')
        except requests.exceptions.HTTPError as err:
            print('Following http error occurred:', err)

    @classmethod
    def get_raw_json_from_html(cls, html):
        print(html)
        div_pos = html.find('class="intro"')
        if not div_pos > 0:
            print('Unexpected HTML Response from Forvo')
            return None
            # raise Exception('Unexpected HTML Response from Forvo')
        pre_open_pos = html.find('pre', div_pos)
        assert pre_open_pos > div_pos
        pre_close_pos = html.find('pre', pre_open_pos + 1)
        assert pre_close_pos > pre_open_pos
        return html[pre_open_pos + 5:pre_close_pos - 3]

    @classmethod
    def normalize_raw_json(cls, raw_json):
        json_str = raw_json.replace('&quot;', '"')
        try:
            return json.loads(json_str)
        except Exception as e:
            print(e)
            raise
            # TODO обработать исключения

    @classmethod
    def get_path_to_mp3_from_json(cls, item):
        mp3_url_key = 'pathmp3'
        return item.get(mp3_url_key).replace('\/', '/')

    def create_word_dir(self):
        dir_path = os.path.join(settings.BASE_DIR, 'media',
                                'sounds', self.word)
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path)
            except PermissionError as e:
                print(e)
                return
        if not os.access(dir_path, os.W_OK):
            return "Permission denied: '{}'".format(dir_path)
        return dir_path

    def create_mp3_full_path(self, dir_path, item_number):
        mp3_file_name = '{}_{}.mp3'.format(self.word, item_number + 1)
        return os.path.join(dir_path, mp3_file_name)

    @classmethod
    def get_mp3_from_forvo(cls, mp3_url):
        try:
            mp3 = requests.get(mp3_url, stream=True)
            if mp3.status_code == 200:
                return mp3.content
        except Exception as e:
            print(e)
            # TODO обработать исключения
            return

    @classmethod
    def save_mp3(cls, mp3_full_path, mp3):
        with open(mp3_full_path, 'wb') as f:
            f.write(mp3)
        return True

    def save_result(self, item, item_number):
        mp3_url = self.get_path_to_mp3_from_json(item)
        word_dir_path = self.create_word_dir()
        if word_dir_path is None:
            return
        mp3_full_path = self.create_mp3_full_path(word_dir_path, item_number)
        mp3 = self.get_mp3_from_forvo(mp3_url)
        mp3_successfully_saved = self.save_mp3(mp3_full_path, mp3)
        if mp3_successfully_saved:
            print(("Pronunciation example number {} for word"
                   " {} successfully saved").format(
                item_number + 1, str(self.word).capitalize()))
        else:
            print('Something went wrong. MP3 has not been saved')

    def import_sound(self):
        html = self.get_html_from_forvo()
        if html is None:
            return
        raw_json = self.get_raw_json_from_html(html)
        if raw_json is None:
            return
        forvo_data = self.normalize_raw_json(raw_json)
        items = forvo_data.get('items', [])
        assert len(items) > 0
        item_number = 0
        for item in items:
            if item['code'] != 'en' or item['country'] != 'United States':
                continue
            self.save_result(item, item_number)
            item_number += 1
            if item_number > 4:
                break


class MultithreadingParser:
    def __init__(self, threads_count=3):
        self.threads_count = threads_count
        self.queue = self._make_queue()

    def _make_queue(self):
        q = queue.Queue()
        for i, word in enumerate(words):
            if ' ' in word:
                continue
            if i == 3:
                break
            # print(word, 'added to queue')
            q.put_nowait(word)
        return q

    def run(self):
        # threads = []
        for i in range(self.threads_count-1):
            thread_name = 'thread_{}'.format(i + 1)
            thread = threading.Thread(
                target=self.worker, args=(thread_name, ), daemon=True)
            thread.start()
        # threads.append(thread)
        # for thread in threads:
        #     thread.join()
        while True:
            if self.queue.qsize() < 1:
                break
            # print('Queue size is {} and {} so far..'.format(
            #    self.queue.qsize(), threading.active_count()))
            time.sleep(1)

    def worker(self, thread_name):
        while True:
            try:
                task = self.queue.get(block=True)
                # print('task, thread_name:', task, thread_name)
                time.sleep(1)
            except queue.Empty:
                return
            fi = ForvoImporter(task)
            try:
                fi.import_sound()
            except Exception as e:
                print(e)
            self.queue.task_done()
