from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from pyvirtualdisplay import Display
from splinter import Browser


class BaseSeleniumTestCase(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not settings.TEST_CLIENTSIDE_CODE:
            return
        if settings.VIRTUAL_DISPLAY:
            display = Display(visible=0, size=(1024, 768))
            display.start()
        cls.browser = Browser('chrome')
        cls.page_object = cls.page_object_class()

    @classmethod
    def tearDownClass(cls):
        if settings.TEST_CLIENTSIDE_CODE:
            cls.browser.quit()
        super().tearDownClass()

    def visit_page(self, path):
        url = '{}{}'.format(self.live_server_url, path)
        self.browser.visit(url)

    def force_login(self, user):
        path = reverse('autologin', kwargs={'id': user.pk})
        self.visit_page(path)
        return user

    def find_element(self, css_selector):
        element = self.browser.find_by_css(css_selector).first
        assert element
        return element
