from django.contrib.auth.decorators import login_required
from django.core.exceptions import SuspiciousOperation
from django.http import Http404, HttpResponseForbidden
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
        preferred_pron = self.kwargs.get('preferred_pron')
        if fieldname_value not in ['meaning', 'pronunciation']:
            raise SuspiciousOperation("Incorrect request")
        if value not in [0, 1]:
            raise SuspiciousOperation("Incorrect request")
        word_data = WordLearningState.objects.filter(id=word_ls_id).first()
        if not word_data:
            raise Http404("Word not found")
        if word_data.user.username != self.request.user.username:
            raise HttpResponseForbidden
        if fieldname_value == 'pronunciation':
            fields_to_update = dict(
                is_user_know_pronunciation=bool(value)
            )
            if value == 1 and preferred_pron:
                fields_to_update['preferred_pronunciation'] = preferred_pron
            WordLearningState.objects.update(**fields_to_update)
        if (fieldname_value == 'meaning' and
                word_data.is_user_know_meaning is not value):
            WordLearningState.objects.update(is_user_know_meaning=value)
        return {}
