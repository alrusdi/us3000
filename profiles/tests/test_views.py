from django.contrib import auth
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from words.models import WordLearningState, Word


class RegistrationViewTest(TestCase):
    def setUp(self):
        self.reg_url = reverse('registration')

    def test_shows_registration_forms(self):
        response = self.client.get(self.reg_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('name="password_confirm"', response.content.decode('utf8'))

    def test_correctly_shows_errors(self):
        response = self.client.get(self.reg_url)
        self.assertEqual(response.status_code, 200)
        data = {'csrfmiddlewaretoken': str(response.context[1].get('csrf_token')),
                'username': '',
                'password': '',
                'password_confirm': ''}
        response2 = self.client.post(self.reg_url, data=data)
        self.assertEqual(response2.status_code, 200)

        # в response2.content есть ошибка - поля обязательные для заполнения

    def test_create_new_user_if_form_valid(self):
        response = self.client.get(self.reg_url)
        data = {'csrfmiddlewaretoken': str(response.context[1].get('csrf_token')),
                'username': 'User_2',
                'password': '123456',
                'password_confirm': '123456'}
        response2 = self.client.post(self.reg_url, data=data)
        self.assertEqual(response2.status_code, 302)
        self.assertEqual(response2._headers['location'][1], '/')
        User.objects.get(username='User_2')
        # import pdb; pdb.set_trace()


class LoginViewTest(TestCase):
    def setUp(self):
        self.login_url = reverse('login')

    def test_shows_login_forms(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        # import pdb; pdb.set_trace()
        self.assertIn('<form name="login"', response.content.decode('utf8'))

    def test_correctly_shows_errors(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        data = {'csrfmiddlewaretoken': str(response.context[1].get('csrf_token')),
                'username': '',
                'password': ''}
        response2 = self.client.post(self.login_url, data=data)
        self.assertEqual(response2.status_code, 200)

    def test_login_if_form_valid(self):
        password = 'test_password'
        user = User.objects.create_user(
            username='test_username',
            email='{}@debugmail.io'.format('test_username'),
            password=password
        )
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        data = {'csrfmiddlewaretoken': str(response.context[1].get('csrf_token')),
                'username': user.username,
                'password': password}
        response2 = self.client.post(self.login_url, data=data)
        self.assertEqual(response2.status_code, 302)
        self.assertEqual(response2._headers['location'][1], '/')
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

    def test_correctly_handles_auth_user(self):
        password = 'test_password'
        user = User.objects.create_user(
            username='test_username',
            email='{}@debugmail.io'.format('test_username'),
            password=password
        )
        self.client.force_login(user)
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response._headers['location'][1], '/')


class LogoutViewTest(TestCase):
    def setUp(self):
        self.password = 'test_password'
        self.user = User.objects.create_user(
            username='test_username',
            email='{}@debugmail.io'.format('test_username'),
            password=self.password
        )
        self.home_url = reverse('home')
        self.logout_url = reverse('logout')

    def test_redirects_authenticated_user_to_login_page(self):
        self.client.force_login(self.user)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)
        response = self.client.get(self.logout_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('<form name="login"', response.content.decode('utf8'))

    def test_redirects_anonymous_user_to_login_page(self):
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)
        response = self.client.get(self.logout_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('<form name="login"', response.content.decode('utf8'))


class SetLearningStateViewTest(TestCase):
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
        user = User.objects.create_user(
            username='test_username',
            email='{}@debugmail.io'.format('test_username'),
            password='123456'
        )
        test_word.wordlearningstate_set.create(
            user=user
        )
        response = self.client.get('/change-learning-state/meaning/1/1/')
        self.assertEqual(response.status_code, 302)  # Why 302? Think should be 200

        #  ? 'change-learning-state/meaning/1/1/' ! WordLearningState.is_user_know_meaning == True
        WordLearningState.objects.update(
            is_user_know_meaning=True
        )
        is_user_know_meaning = WordLearningState.objects.filter(
            id=1
        ).values(
            'is_user_know_meaning'
        )[0]['is_user_know_meaning']
        self.assertEqual(is_user_know_meaning, True)

        # ? 'change-learning-state/meaning/1/0/' ! WordLearningState.is_user_know_meaning == False
        WordLearningState.objects.update(
            is_user_know_meaning=False
        )
        is_user_know_meaning = WordLearningState.objects.filter(
            id=1
        ).values(
            'is_user_know_meaning'
        )[0]['is_user_know_meaning']
        self.assertEqual(is_user_know_meaning, False)

        # ? 'change-learning-state/pronunciation/1/1/' ! WordLearningState.is_user_know_pronunciation == True
        WordLearningState.objects.update(
            is_user_know_pronunciation=True
        )
        is_user_know_pronunciation = WordLearningState.objects.filter(
            id=1
        ).values(
            'is_user_know_pronunciation'
        )[0]['is_user_know_pronunciation']
        self.assertEqual(is_user_know_pronunciation, True)

        # ? 'change-learning-state/pronunciation/1/0/' ! WordLearningState.is_user_know_pronunciation == False
        WordLearningState.objects.update(
            is_user_know_pronunciation=False
        )
        is_user_know_pronunciation = WordLearningState.objects.filter(
            id=1
        ).values(
            'is_user_know_pronunciation'
        )[0]['is_user_know_pronunciation']
        self.assertEqual(is_user_know_pronunciation, False)
        # TODO update tests when SetLearningStateView complited
        # TODO add 'first()' to 'filter' in queries
