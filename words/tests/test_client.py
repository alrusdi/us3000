import os
from datetime import date
from django.contrib.auth.models import User
from main.base_selenium_test_case import BaseSeleniumTestCase
from main.settings import BASE_DIR


class IndexPageObject:
    def __init__(self):
        self.show_meanings_link = "a[data=test-show-meanings-link]"
        self.meanings_container = "div[data=test-meanings-values]"


class IndexTest(BaseSeleniumTestCase):
    page_object_class = IndexPageObject

    def test_show_meanings(self):
        password = 'test12345678'
        user = User.objects.create_user(
            username='test_username',
            email='{}@debugmail.io'.format('test_username'),
            password=password
        )
        self.force_login(user)
        link = self.find_element(self.page_object.show_meanings_link)
        link.click()
        meanings_container = self.find_element(self.page_object.meanings_container)
        assert meanings_container.visible

    def test_show_main_page(self):
        screenshot_name = '{}_{}_'.format(__name__, date.today())
        screenshot_path = os.path.join(
            os.path.join(BASE_DIR, 'words', 'tests',
                         'screenshots', screenshot_name))
        password = 'test12345678'
        user = User.objects.create_user(
            username='test_username',
            email='{}@debugmail.io'.format('test_username'),
            password=password
        )
        self.force_login(user)
        self.browser.screenshot(screenshot_path)
