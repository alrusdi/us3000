from django.conf import settings
from django.test import TestCase, override_settings
from fudge.inspector import arg

from words.management.commands._od_importer import ODImporter
import fudge


class FakeRequestsResponse:
    def __init__(self, text, status_code=200):
        self.text = text
        self.status_code = status_code

    def raise_for_status(self):
        pass



class ODImporterTest(TestCase):
    @fudge.patch('words.management.commands._od_importer.requests.get')
    @override_settings(OXFORD_DICTIONARY_APP_ID_1='test_app_id',
                       OXFORD_DICTIONARY_APP_KEY_1='test_app_key')
    def test_uses_requests_to_get_article_from_od(self, fake_get):
        url = 'od-api.oxforddictionaries.com'
        expected_headers = {'app_id': 'test_app_id', 'app_key': 'test_app_key'}
        fake_get.expects_call().with_args(arg.contains(
            url), headers=expected_headers).returns(FakeRequestsResponse('{}'))
        test_word = ODImporter('something')
        msg, res = test_word.get_article(settings.OXFORD_DICTIONARY_APP_ID_1,
                                         settings.OXFORD_DICTIONARY_APP_KEY_1)
        self.assertEqual(msg, 'Data successfully saved')

    def test_2(self):
        #Что будет если произойдет Connection Error
        # raises - передать исключение
        print('Test2')

    def test_3(self):
        # Что будет если вернется 404
        pass

    def test_4(self):
        # Что будет если вернется другая http ошибка
        pass

    def test_positive_case(self):
        # Что будет если корректные параметры переданы и ошибок не произошло
        pass

    def test_5(self):
        # Убедиться что функция 'create_word_article' сохраняет файлы в нужную директорию
        pass

    def test_6(self):
        # что будет если директория недоступна на запись
        pass

    def test_7(self):
        # Что будет если abs_path_dir == None
        pass


class ForvoImporterTest(TestCase):
    def setUp(self):
        print('FVSetup')

    @classmethod
    def setUpClass(cls):
        print('FVSetupClass')

    def tearDown(self):
        print('FVtearDown')

    @classmethod
    def tearDownClass(cls):
        print('FVtearDownClass')

    def test_test(self):
        print('FVTest')

    def test_test2(self):
        print('FVTest2')
