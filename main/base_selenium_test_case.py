from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from pyvirtualdisplay import Display
from splinter import Browser


class BaseSeleniumTestCase(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if settings.VIRTUAL_DISPLAY:
            display = Display(visible=0, size=(800, 600))
            display.start()
        cls.browser = Browser('chrome')
        cls.page_object = cls.page_object_class()

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()

    def force_login(self, user):
        url = '{}{}'.format(self.live_server_url, reverse('autologin', kwargs={'id': user.pk}))
        self.browser.visit(url)
        return user

    def find_element(self, css_selector):
        element = self.browser.find_by_css(css_selector).first
        assert element
        return element
