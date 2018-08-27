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

    def import_sound(self):
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
        result = requests.post(url, data=data)
        # TODO Проверить корректность ответа (статус 200)
        html = str(result.content)
        div_pos = html.find('class="intro"')
        if not div_pos > 0:
            raise Exception('Unexpected HTML Response from Forvo')
        pre_open_pos = html.find('pre', div_pos)

        assert pre_open_pos > div_pos
        pre_close_pos = html.find('pre', pre_open_pos + 1)
        assert pre_close_pos > pre_open_pos
        raw_json = html[pre_open_pos + 5:pre_close_pos - 3]
        json_str = raw_json.replace('&quot;', '"')
        try:
            forvo_data = json.loads(json_str)
        except Exception as e:
            print(e)
            raise
            # TODO обработать исключения
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

    def save_result(self, item, item_number):
        mp3_path = item.get('pathmp3').replace('\/', '/')
        file_name = '{}_{}.mp3'.format(self.word, item_number + 1)
        dir_path = os.path.join(settings.BASE_DIR, 'media',
                                'sounds', self.word)
        full_path = '{}/{}'.format(dir_path, file_name)

        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        try:
            mp3 = requests.get(mp3_path, stream=True)
        except Exception as e:
            print(e)
            # TODO обработать исключения
            raise
        if mp3.status_code == 200:
            with open(full_path, 'wb') as f:
                f.write(mp3.content)
            print(("Pronunciation example number {} for word"
                   " {} successfully saved").format(
                item_number + 1, str(self.word).capitalize()))


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
