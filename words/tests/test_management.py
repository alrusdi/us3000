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

    @fudge.patch('words.management.commands._od_importer.requests.get')
    def test_uses_requests_to_raise_connection_error(self, fake_get):
        fake_get.expects_call().raises(requests.exceptions.ConnectionError)
        test_word = ODImporter('second')
        msg, res = test_word.get_article('', '')
        self.assertEqual(msg, 'Connection error')

    @fudge.patch('words.management.commands._od_importer.requests.get')
    def test_uses_requests_to_raise_404_error(self, fake_get):
        http_error = 404
        fake_get.expects_call().raises(requests.exceptions.HTTPError(http_error))
        test_word = ODImporter('third')
        msg, res = test_word.get_article('', '')
        self.assertEqual(msg, 'Specified word does not exist in Oxford Dictionary')

    @fudge.patch('words.management.commands._od_importer.requests.get')
    def test_uses_requests_to_raise_not_404_http_error(self, fake_get):
        http_error = 418
        fake_get.expects_call().raises(requests.exceptions.HTTPError(http_error))
        test_word = ODImporter('fourth')
        msg, res = test_word.get_article('', '')
        self.assertEqual(msg, 'HTTP error {} occurred'.format(
            requests.exceptions.HTTPError(http_error)))

    def test_positive_case(self):
        # Что будет если корректные параметры переданы и ошибок не произошло
        pass

    def test_5(self):
        # Убедиться что функция 'create_word_article' сохраняет файлы в нужную директорию
        pass

    @fudge.patch('words.management.commands._od_importer.os.path.exists')
    @fudge.patch('words.management.commands._od_importer.os.access')
    def test_write_permissions_of_working_dir(self, fake_path_exists,
                                              fake_dir_access):
        fake_path_exists.expects_call().returns(True)
        fake_dir_access.expects_call().returns(False)
        test_word = ODImporter('sixth')
        msg = test_word.create_word_article('', '', '')
        self.assertEqual(msg, "Permission denied: ''")

    @fudge.patch('words.management.commands._od_importer.os.path.exists')
    def test_is_working_dir_exist(self, fake_path_exists):
        fake_path_exists.expects_call().returns(False)
        test_word = ODImporter('seventh')
        msg = test_word.create_word_article('', '', '')
        self.assertEqual(msg, "Path does not exist: ''")


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
