import datetime
import random

from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from main.settings import WORDS_NUMBER, WORDS_TO_REPEAT_BOUND, WORDS_NUMBER_TO_REPEAT
from main.views import JsonView
from words.models import Word, WordLearningState


@method_decorator(login_required, name='dispatch')
class IndexView(TemplateView):
    template_name = "words/index.html"


@method_decorator(login_required, name='dispatch')
class LearningStateView(JsonView):
    def get_known_words_ids(self):
        # получаем список id изученных слов данного пользователя:
        return WordLearningState.objects.filter(
            user=self.request.user,
            is_user_know_meaning=True,
            is_user_know_pronunciation=True
        ).values_list(
            'id', flat=True
        )

    def get_all_words_ids(self):
        # получаем id всех слов:
        return Word.objects.filter(
            is_active=True
        ).values_list(
            'id', flat=True
        )

    def calculate_new_known_words_ratio(self, known_words_number, all_words_number):
        if known_words_number < WORDS_TO_REPEAT_BOUND:
            known_words_needed = 0
            new_words_needed = WORDS_NUMBER
        elif all_words_number - known_words_number > WORDS_NUMBER - WORDS_NUMBER_TO_REPEAT:
            new_words_needed = WORDS_NUMBER - WORDS_NUMBER_TO_REPEAT
            known_words_needed = WORDS_NUMBER_TO_REPEAT
        elif all_words_number - known_words_number < WORDS_NUMBER - WORDS_NUMBER_TO_REPEAT:
            new_words_needed = all_words_number - known_words_number
            known_words_needed = WORDS_NUMBER - new_words_needed
        else:
            raise Exception('unexpected words ratio')
        return known_words_needed, new_words_needed

    def save_word_learning_state_to_db(self, needed_ids, user):
        new_states = []
        # для каждого из этих N создаем объект LearningState
        # сохраняем в список
        for id in needed_ids:
            if WordLearningState.objects.filter(word_id=id, user=user).update(usage_count=F('usage_count') + 1):
                # WordLearningState.objects.all().update(is_user_know_meaning=True, is_user_know_pronunciation=True)
                continue
            new_states.append(WordLearningState(user=user, word_id=id, usage_count=1))  # именованые аргументы
        # сохраняем массовой загрузкой в БД
        # https://docs.djangoproject.com/en/dev/ref/models/querysets/#bulk-create
        WordLearningState.objects.bulk_create(new_states)

    def get_random_new_words(self, known_words_ids, all_words_ids, new_words_needed):
        # из списка всех слов вычитаем список изученных
        new_ids = set(all_words_ids) - set(known_words_ids)
        # получаем N случайных из них
        needed_ids = random.sample(new_ids, new_words_needed)
        return list(needed_ids)

    def get_words_to_repeat(self, number_words_to_repeat):
        words = WordLearningState.objects.filter(
            user=self.request.user,
            is_user_know_meaning=True,
            is_user_know_pronunciation=True
        ).order_by(
            'usage_count'
        ).values_list(
            'id', flat=True
        )
        words = words[:number_words_to_repeat]
        return list(words)

    def get_context_data(self):
        known_words_ids = self.get_known_words_ids()
        all_words_ids = self.get_all_words_ids()
        known_words_needed, new_words_needed = self.calculate_new_known_words_ratio(
            len(known_words_ids),
            len(all_words_ids)
        )
        random_new_words = self.get_random_new_words(known_words_ids, all_words_ids, new_words_needed)
        self.save_word_learning_state_to_db(random_new_words, self.request.user)
        words_to_repeat = self.get_words_to_repeat(known_words_needed)
        words_for_learning = random_new_words + words_to_repeat
        random.shuffle(words_for_learning)
        qs = WordLearningState.objects.filter(
            pk__in=words_for_learning
        ).prefetch_related(
            'word',
            'word__pronunciation_set',
            'word__meaning_set'
        )
        words_data_list = []
        for word in qs:
            words_data_list.append(serialize_learning_state(word))
            # word_data = []
        #     word_data.extend(*Word.objects.filter(id=word).values_list('id', 'value'))
        #     word_data.append(*WordLearningState.objects.filter(word_id=word).values_list('id', flat=True))
        #     words_data_list.append(dict(zip(('id', 'value', 'learning_state_id'), word_data)))
        return {"words": words_data_list}
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


@method_decorator(login_required, name='dispatch')
class SetLearningStateView(JsonView):
    def get_context_data(self):
        fieldname = self.kwargs.get('fieldname')
        value = self.kwargs.get('value')
        id = self.kwargs.get('id')
        if self.kwargs.get('fieldname') not in ['meaning', 'pronunciation']:
            print(111111111)
            raise #ValidationError('')
        if self.kwargs.get('value') not in [0, 1]:
            print(22222222222)
            raise #ValidationError('')
        word_data = WordLearningState.objects.filter(id=self.kwargs.get('id')).first()
        if not word_data:
            print(3333333333333333)
            raise #ValidationError('')
        if word_data.user.username != self.request.user.username:
            print(44444444444)
        if (self.kwargs.get('fieldname') == 'pronunciation' and
                word_data.is_user_know_pronunciation is not self.kwargs.get('value')):
            WordLearningState.objects.update(is_user_know_pronunciation=self.kwargs.get('value'))
        if (self.kwargs.get('fieldname') == 'meaning' and
                word_data.is_user_know_meaning is not self.kwargs.get('value')):
            WordLearningState.objects.update(is_user_know_meaning=self.kwargs.get('value'))

        # Проверить входит ли поле <fieldname> in [meaning, pronunciation]
        # Убедиться что value == 0 или 1
        # Должна принемать параметр WordLearningState.id и убедиться что принадлежит
        # именно текущему пользователю - если нет - ошибка
        # Назначить нужному полю нужное значение
        # Если да, то поставить is_user_know_meaning в True

        return {}


        # import pdb; pdb.set_trace()












