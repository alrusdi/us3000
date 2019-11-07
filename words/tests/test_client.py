from django.conf import settings
from django.contrib.auth.models import User
from django.test import override_settings

from main.base_selenium_test_case import BaseSeleniumTestCase


class IndexPageObject:
    def __init__(self):
        self.show_meanings_link = "a[data=test-show-meanings-link]"
        self.meanings_container = "div[data=test-meanings-values]"


class IndexTest(BaseSeleniumTestCase):
    page_object_class = IndexPageObject

    @override_settings(
        DEBUG=True
    )
    def test_show_meanings(self):
        if not settings.TEST_CLIENTSIDE_CODE:
            return
        password = 'test12345678'
        user = User.objects.create_user(
            username='test_username',
            email='{}@debugmail.io'.format('test_username'),
            password=password
        )

        self.force_login(user)
        self.visit_page('/')
        link = self.find_element(self.page_object.show_meanings_link)
        link.click()
        meanings_container = self.find_element(self.page_object.meanings_container)
        assert meanings_container.visible
