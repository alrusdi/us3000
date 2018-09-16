import datetime
import random

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from main.settings import WORDS_NUMBER
from main.views import JsonView
from words.models import Word, WordLearningState


@method_decorator(login_required, name='dispatch')
class IndexView(TemplateView):
    template_name = "words/index.html"


@method_decorator(login_required, name='dispatch')
class LearningStateView(JsonView):
    def get_context_data(self):
        random_new_words = self.get_random_new_words()
        words_to_repeat = self.get_words_to_repeat(5)
        return {'a': words_to_repeat, 'b': datetime.datetime.now(), 'c': 'привет'}
        # 1. Если у пользователя нет изученных слов - показываем ему settings.WORDS_NUMBER случайных
        # 2. Если у пользователя есть изученные слова, то показываем ему settings.WORDS_NUMBER слов, состоящих из
        # N случайных новых слов и M слов на повторение, где M > 0, если всего изученных слов больше или равно
        # settings.WORDS_TO_REPEAT_BOUND
        # 3.

        # 1. Получаем сумму изученных слов:
        # number_known_words = LearningState.objects.filter(user=self.request.user, is_user_know_meaning=True, is_user_know_pronunciation=True).count()
        #
        # 2. Если number_known_words < settings.WORDS_TO_REPEAT_BOUND, то возвращаем Settings.WORDS_NUMBER случайных
        # 3. settings.WORDS_NUMBER - settings.WORDS_TO_REPEAT
        # 4. Перемешать и вернуть json: {'id': id, 'learning_state_id': id, 'value': word}

    def get_random_new_words(self):
        user = self.request.user
        # получаем id всех слов:
        word_ids = Word.objects.filter(is_active=True).values_list('id', flat=True)
        # получаем список id изученных слов данного пользователя:
        known_words_ids = WordLearningState.objects.filter(
            user=self.request.user,
            is_user_know_meaning=True,
            is_user_know_pronunciation=True
        ).values_list('id', flat=True)
        #
        # из списка всех слов вычитаем список изученных
        new_ids = set(word_ids) - set(known_words_ids)
        # получаем N случайных из них
        needed_ids = random.sample(new_ids, WORDS_NUMBER)
        # для каждого из этих N создаем объект LearningState
        new_states = []
        for id in needed_ids:
            new_states.append(WordLearningState(user=user, word_id=id, usage_count=1))  #  именованые аргументы
        # возвращаем список этих N объектов
        # https://docs.djangoproject.com/en/dev/ref/models/querysets/#bulk-create
        WordLearningState.objects.bulk_create(new_states)
        return str(new_states)

    def get_words_to_repeat(self, number_words_to_repeat):
        words = WordLearningState.objects.filter(
            user=self.request.user,
            is_user_know_meaning=True,
            is_user_know_pronunciation=True
        ).order_by('usage_count')
        words = words[:number_words_to_repeat]
        return str(words)













