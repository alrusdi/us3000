from django.db import models


class Word(models.Model):
    value = models.CharField(
        max_length=50,
        verbose_name='Слово'
    )
    meaning = models.TextField(
        verbose_name='Значение'
    )
    spelling = models.CharField(
        max_length=250,
        verbose_name='Транскрипция'
    )
    raw_od_article = models.TextField(
        verbose_name='Сырые данные с OD'
    )

    def __str__(self):
        return self.value

    class Meta:
        ordering = ["value"]
        verbose_name = "Слово"
        verbose_name_plural = "Слова"


class Pronunciation(models.Model):
    word = models.ForeignKey(
        Word,
        on_delete=models.CASCADE,
        verbose_name='Слово'
    )
    audio = models.CharField(
        max_length=250,
        verbose_name='Произношение'
    )
    raw_od_data = models.TextField(
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

    def __str__(self):
        return "Статистика слова {}".format(self.word)

    class Meta:
        verbose_name = "Статистика"
        verbose_name_plural = "Статистика"
