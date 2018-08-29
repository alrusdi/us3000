from django.contrib import admin
from django.db import models
from django.forms.widgets import Input
from words.models import Word, Pronunciation, Meaning, WordLearningState


class AudioWidget(Input):
    def render(self, name, value, attrs=None, renderer=None):
        html = super(AudioWidget, self).render(name, value, attrs, renderer)
        html = ('<div style="display: none">{}</div>'
                '<audio src="/media/{}" controls></audio>').format(html,
                                                                   value)
        return html


class PronunciationInline(admin.StackedInline):
    model = Pronunciation
    max_num = 1
    formfield_overrides = {
        models.FileField: {'widget': AudioWidget}
    }


class MeaningInline(admin.TabularInline):
    model = Meaning
    max_num = 1


class WordLearningStateInline(admin.TabularInline):
    model = WordLearningState
# TODO для данного класса сделать отдельную админку


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    inlines = (
        MeaningInline,
        PronunciationInline,
        WordLearningStateInline,
    )
