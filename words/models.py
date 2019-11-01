import json
import os

from django.conf import settings
from django.db import models
from jsonfield import JSONField


class Word(models.Model):
    value = models.CharField(
        max_length=50,
        verbose_name='Слово'
    )
    spelling = models.CharField(
        max_length=250,
        verbose_name='Транскрипция'
    )
    raw_od_article = JSONField(
        verbose_name='Сырые данные с OD'
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='Используется'
    )

    def __str__(self):
        return self.value

    class Meta:
        ordering = ["value"]
        verbose_name = "Слово"
        verbose_name_plural = "Слова"


class Meaning(models.Model):
    word = models.ForeignKey(
        Word,
        on_delete=models.CASCADE,
        verbose_name='Слово'
    )
    value = models.TextField(
        verbose_name='Значение'
    )
    order = models.PositiveIntegerField(
        verbose_name="Порядок",
        default=0
    )
    examples = JSONField(
        null=True,
        blank=True
    )

    def __str__(self):
        if self.value is None:
            return ''
        return self.value[:20]

    class Meta:
        ordering = ["order"]
        verbose_name = "Доп. значение"
        verbose_name_plural = "Доп. значения"


class Pronunciation(models.Model):
    word = models.ForeignKey(
        Word,
        on_delete=models.CASCADE,
        verbose_name='Слово'
    )
    audio = models.FileField(
        upload_to='media/audio',
        verbose_name='Произношение'
    )
    raw_od_data = JSONField(
        verbose_name='Сырые данные с OD',
        blank=True,
        null=True
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Используется'
    )

    def __str__(self):
        return "Произношение {}".format(self.word)

    class Meta:
        verbose_name = "Произношение"
        verbose_name_plural = "Произношения"


class PronunciationMeta(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

class WordLearningState(models.Model):
    word = models.ForeignKey(
        Word,
        on_delete=models.CASCADE,
        verbose_name='Слово'
    )
    user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    is_user_know_meaning = models.BooleanField(
        default=False,
        verbose_name='Выучил значение'
    )
    is_user_know_pronunciation = models.BooleanField(
        default=False,
        verbose_name='Выучил произношение'
    )
    usage_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Количество показов'
    )
    last_usage_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата последнего показа'
    )
    preferred_pronunciation = models.PositiveIntegerField(
        default=0,
        verbose_name='forvo id препочтительного произношения',
    )
    training_session = models.BooleanField(
        default=False,
        blank=False,
        verbose_name='Сеанс обучения'
    )

    def _get_pronunciations_meta(self, word_str):
        forvo_meta_path = os.path.join(
            settings.BASE_DIR, 'media', 'forvo', '{}.json'.format(word_str)
        )
        if not os.path.exists(forvo_meta_path):
            return
        with open(forvo_meta_path, 'r') as f:
            data = json.load(f)
        return data

    def _get_sounds(self, word_str):
        ret = []
        sounds_path = os.path.join(settings.BASE_DIR, 'media', 'sounds', word_str)
        print(sounds_path)
        if not os.path.exists(sounds_path):
            return []
        items = list(os.listdir(sounds_path))
        items.sort()
        for item in items:
            if item.endswith('.mp3'):
                ret.append('{}{}/{}/{}'.format(settings.MEDIA_URL, 'sounds', word_str, item))
        return ret

    def get_pronunciations(self):
        word = self.word
        forvo_meta = self._get_pronunciations_meta(word.value)
        if not forvo_meta:
            return []

        ret = []
        ct = 0
        sounds = self._get_sounds(word.value)
        slen = len(sounds)
        prefered_detected = False
        for item in forvo_meta.get('items') or []:

            if item.get('code', '') != 'en' or item.get(
                    'country', '') != 'United States':
                continue

            if ct > slen-1:
                break

            sound_file = sounds[ct]

            is_best = self.preferred_pronunciation == item['id']

            if is_best:
                prefered_detected = True

            ret.append({
                'id': item['id'],
                'by': item['username'],
                'sex': item['sex'],
                'src': sound_file,
                'best': is_best
            })

            ct += 1
            if ct == 4:
                break
        if ret and not prefered_detected:
            ret[0]['best'] = True
        return ret

    def __str__(self):
        return "Статистика слова {}".format(self.word)

    class Meta:
        verbose_name = "Статистика"
        verbose_name_plural = "Статистика"
