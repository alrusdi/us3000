from django.contrib.auth.decorators import login_required
from django.core.exceptions import SuspiciousOperation
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from main.views import JsonView
from words._ls_utils import get_words_qs
from words.models import WordLearningState
from words.serializer import serialize_learning_state


@method_decorator(login_required, name='dispatch')
class IndexView(TemplateView):
    template_name = "words/index.html"


@method_decorator(login_required, name='dispatch')
class LearningStateView(JsonView):
    def get_context_data(self):
        user = self.request.user
        qs = get_words_qs(user)
        words_data_list = []
        for word in qs:
            words_data_list.append(serialize_learning_state(word))
        return {"words": words_data_list}


@method_decorator(login_required, name='dispatch')
class SetLearningStateView(JsonView):
    def get_context_data(self):
        fieldname_value = self.kwargs.get('fieldname')
        value = self.kwargs.get('value')
        word_ls_id = self.kwargs.get('id')
        if fieldname_value not in ['meaning', 'pronunciation']:
            raise SuspiciousOperation("Incorrect request")
        if value not in [0, 1]:
            raise SuspiciousOperation("Incorrect request")
        word_data = WordLearningState.objects.filter(id=word_ls_id).first()
        if not word_data:
            raise SuspiciousOperation("Incorrect request")
        if word_data.user.username != self.request.user.username:
            raise SuspiciousOperation("Incorrect request")
        if (fieldname_value == 'pronunciation' and
                word_data.is_user_know_pronunciation is not value):
            WordLearningState.objects.update(is_user_know_pronunciation=value)
        if (fieldname_value == 'meaning' and
                word_data.is_user_know_meaning is not value):
            WordLearningState.objects.update(is_user_know_meaning=value)
        return {}
        # Проверить входит ли поле <fieldname> in [meaning, pronunciation]
        # Убедиться что value == 0 или 1
        # Должна принемать параметр WordLearningState.id и убедиться что принадлежит
        # именно текущему пользователю - если нет - ошибка
        # Назначить нужному полю нужное значение
        # Если да, то поставить is_user_know_meaning в True


