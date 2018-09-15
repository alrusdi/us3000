import datetime
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from main.views import JsonView


@method_decorator(login_required, name='dispatch')
class IndexView(TemplateView):
    template_name = "words/index.html"


@method_decorator(login_required, name='dispatch')
class LearningStateView(JsonView):
    def get_context_data(self):
        return {'a': 1.3, 'b': datetime.datetime.now(), 'c': 'привет'}
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
        # word_ids = Word.objects.filter(is_active=True).values_list('id', flat=True)
        # получаем список id изученных слов данного пользователя:
        #
        # known_words_ids = ...
        #
        # из списка всех слов вычитаем список изученных
        # new_ids = set(word_ids) - set(known_words_ids)
        # волучаем случайные N из них
        # needed_ids = randon.choise(new_ids)
        # для каждого из этих N создаем объект LearningState
        new_states = []
        for id in needed_ids:
            new_states.append(LearningState(user=user, ...)) # именованые аргументы
        # возвращаем список этих N объектов
        # https://docs.djangoproject.com/en/dev/ref/models/querysets/#bulk-create
        LearningState.objects.bulk_create(new_states)
        pass

    def get_words_to_repeat(self, number_words_to_repeat):
        words = LearningState.objects.filter(
            user=self.request.user,
            is_user_know_meaning=True,
            is_user_know_pronunciation=True
        ).order_by('usage_count')
        words = words[:number_words_to_repeat]
        return list(words)













