from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class RegistrationViewTest(TestCase):
    def setUp(self):
        self.reg_url = reverse('registration')

    def test_shows_registration_forms(self):
        response = self.client.get(self.reg_url)
        # import pdb; pdb.set_trace()
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


