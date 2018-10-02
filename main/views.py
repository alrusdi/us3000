import json
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.views import View


class JsonView(View):
    def dispatch(self, request, *args, **kwargs):
        super().dispatch(request, *args, **kwargs)
        context = self.get_context_data()
        data = json.dumps(context, sort_keys=True, ensure_ascii=False, indent=4, cls=DjangoJSONEncoder)
        return HttpResponse(data, content_type='application/json')

    def get_context_data(self):
        return {}
