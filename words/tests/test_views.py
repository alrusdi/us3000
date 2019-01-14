from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from words.models import WordLearningState, Word


class SetLearningStateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test_username',
            email='{}@debugmail.io'.format('test_username'),
            password='123456'
        )
        self.client.force_login(self.user)

    def test_assigns_correct_values_to_given_fields(self):
        test_word = Word.objects.create(
            value='test_word',
            spelling='spelling',
            raw_od_article='raw_od_article'
        )
        test_word.pronunciation_set.create(
            audio='test_mp3'
        )
        test_word.meaning_set.create(
            value='test_value'
        )
        test_word.wordlearningstate_set.create(
            user=self.user
        )

        #  ? 'change-learning-state/meaning/1/1/' ! WordLearningState.is_user_know_meaning == True
        response = self.client.get('/change-learning-state/meaning/1/1/0/')
        self.assertEqual(response.status_code, 200)
        is_user_know_meaning = WordLearningState.objects.filter(
            id=1
        ).first().is_user_know_meaning
        self.assertEqual(is_user_know_meaning, True)

        # ? 'change-learning-state/meaning/1/0/' ! WordLearningState.is_user_know_meaning == False
        response = self.client.get('/change-learning-state/meaning/1/0/0/')
        self.assertEqual(response.status_code, 200)
        is_user_know_meaning = WordLearningState.objects.filter(
            id=1
        ).first().is_user_know_meaning
        self.assertEqual(is_user_know_meaning, False)

        # ? 'change-learning-state/pronunciation/1/1/' ! WordLearningState.is_user_know_pronunciation == True
        response = self.client.get('/change-learning-state/pronunciation/1/1/0/')
        self.assertEqual(response.status_code, 200)
        is_user_know_pronunciation = WordLearningState.objects.filter(
            id=1
        ).first().is_user_know_pronunciation
        self.assertEqual(is_user_know_pronunciation, True)

        # ? 'change-learning-state/pronunciation/1/0/' ! WordLearningState.is_user_know_pronunciation == False
        response = self.client.get('/change-learning-state/pronunciation/1/0/0/')
        self.assertEqual(response.status_code, 200)
        is_user_know_pronunciation = WordLearningState.objects.filter(
            id=1
        ).first().is_user_know_pronunciation
        self.assertEqual(is_user_know_pronunciation, False)

    def test_wrong_request_sent(self):
        response = self.client.get('/change-learning-state/some-wrong-value/1/0/0/')
        self.assertEqual(response.status_code, 400)

        response = self.client.get('/change-learning-state/meaning/2/0/0/')
        self.assertEqual(response.status_code, 404)

        response = self.client.get('/change-learning-state/pronunciation/1/3/0/')
        self.assertEqual(response.status_code, 400)

    def test_sets_preferred_pronunciations(self):
        test_word = Word.objects.create(
            value='test_word',
            spelling='spelling',
            raw_od_article='raw_od_article'
        )
        ls = test_word.wordlearningstate_set.create(
            user=self.user
        )
        self.assertEqual(ls.preferred_pronunciation, 0)
        url = reverse('set_learning_state', kwargs={'fieldname': 'pronunciation',
                                                    'id': ls.pk,
                                                    'value': 1,
                                                    'preferred_pron': '123456'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        ls.refresh_from_db()
        self.assertEqual(ls.preferred_pronunciation, 123456)

    def test_does_not_set_unexpected_pronunciation(self):
        #  Проверить что не устанавливается несуществующее произношение
        pass

    def test_does_not_set_pronunciation_from_another_word(self):
        # не устанавливает произношение другого слова
        pass

    def test_does_not_set_pronunciation_for_word_which_user_does_not_know(self):
        pass

    def test_user_can_not_change_ls_of_other_users(self):
        pass

    def test_optimization(self):
        pass
        # найти метод который смотрит все запросы к БД и если есть лищний - то ругается

    def test_sets_only_given_word(self):
        # создать несколько word learning states, сходить по url set learning state,
        # убедиться, что обновилась только одна нужная запись
        pass
